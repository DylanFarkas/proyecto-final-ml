import pandas as pd
import numpy as np
from arch import arch_model
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import os
import ray

# -------------------------
# CARGA DE DATOS
# -------------------------
def cargar_datos_diarios(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df['log_ret'] = np.log(df['Adj Close']).diff()
    return df

def cargar_datos_intradia(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    df['date'] = pd.to_datetime(df.index.date)
    return df

# -------------------------
# GARCH y señales diarias (con Ray)
# -------------------------
@ray.remote
def predecir_varianza_garch(x):
    model = arch_model(y=x, p=1, q=3)
    fitted = model.fit(update_freq=5, disp='off')
    return fitted.forecast(horizon=1).variance.iloc[-1, 0]

def generar_senal_diaria(df):
    df = df.copy()
    df['variance'] = df['log_ret'].rolling(180).var()
    df = df['2020-01-01':].copy()

    ventanas = [df['log_ret'].iloc[i-180:i] for i in range(180, len(df)+1)]
    futures = [predecir_varianza_garch.remote(v) for v in ventanas]
    resultados = ray.get(futures)

    df.loc[df.index[179:], 'predictions'] = resultados
    df['prediction_premium'] = (df['predictions'] - df['variance']) / df['variance']
    df['premium_std'] = df['prediction_premium'].rolling(180).std()
    df['signal_daily'] = df.apply(
        lambda x: 1 if x['prediction_premium'] > 1.5 * x['premium_std'] else 
                  (-1 if x['prediction_premium'] < -1.5 * x['premium_std'] else np.nan), axis=1)
    df['signal_daily'] = df['signal_daily'].shift()
    return df

# -------------------------
# Señales intradía (RSI + Bollinger)
# -------------------------
def generar_senal_intradia(intraday_df, senales_diarias):
    df = intraday_df.reset_index()\
            .merge(senales_diarias[['signal_daily']].reset_index(), left_on='date', right_on='Date')\
            .set_index('datetime')
    df = df.drop(['date', 'Date'], axis=1)

    rsi = RSIIndicator(close=df['close'], window=20)
    df['rsi'] = rsi.rsi()

    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    df['lband'] = bb.bollinger_lband()
    df['uband'] = bb.bollinger_hband()

    def signal(row):
        if row['rsi'] > 70 and row['close'] > row['uband']:
            return 1
        elif row['rsi'] < 30 and row['close'] < row['lband']:
            return -1
        else:
            return np.nan

    df['signal_intraday'] = df.apply(signal, axis=1)

    # Señal combinada como en el notebook
    def combinacion(row):
        if row['signal_daily'] == 1 and row['signal_intraday'] == 1:
            return -1
        elif row['signal_daily'] == -1 and row['signal_intraday'] == -1:
            return 1
        else:
            return np.nan

    df['return_sign'] = df.apply(combinacion, axis=1)
    df['return_sign'] = df.groupby(pd.Grouper(freq='D'))['return_sign'].transform(lambda x: x.ffill())
    return df

# -------------------------
# Retorno final
# -------------------------
def calcular_retorno_final(df):
    df = df.copy()
    df['return'] = df['close'].pct_change()
    df['forward_return'] = df['return'].shift(-1)
    df['strategy_return'] = df['forward_return'] * df['return_sign']

    # Acumulado exponencial como en el notebook
    df['strategy_return'] = df['strategy_return'].fillna(0)
    df['cumulative_strategy_return'] = np.exp(np.log1p(df['strategy_return']).cumsum()) - 1
    return df
