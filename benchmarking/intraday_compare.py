import time
from matplotlib import pyplot as plt
import ray
import pandas as pd
import numpy as np
import psutil
import threading
import os
import sys
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from arch import arch_model

from ray_task.intraday import load_intraday_data, predict_variance_garch, generate_daily_signal, generate_signal_intradia, calculate_final_return, load_daily_data

def measure_cpu_usage(interval=1, duration=3):
    cpu_readings = [psutil.cpu_percent(interval=interval) for _ in range(duration)]
    return np.mean(cpu_readings)

# Función para manejar timeout y consultar al usuario (compatible con Windows)
class TimeoutManager:
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds
        self.should_continue = True
        self.timer = None
        self.timeout_occurred = False
        
    def timeout_callback(self):
        """Callback que se ejecuta cuando se alcanza el timeout"""
        self.timeout_occurred = True
        print(f"\n⚠️  ADVERTENCIA: La operación ha tardado más de {self.timeout_seconds} segundos.")
        print("Esto puede indicar que el proceso está tomando más tiempo del esperado.")
        
        try:
            response = input("¿Desea continuar con la ejecución? (s/n): ").lower().strip()
            if response in ['n', 'no']:
                print("🛑 Operación cancelada por el usuario.")
                self.should_continue = False
                # Forzar la salida del programa
                os._exit(1)
            else:
                print("✅ Continuando con la ejecución...")
                # Reiniciar el timer para el siguiente check
                self.start_timer()
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 Operación interrumpida por el usuario.")
            self.should_continue = False
            os._exit(1)
    
    def start_timer(self):
        """Inicia el timer de timeout"""
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout_seconds, self.timeout_callback)
        self.timer.daemon = True
        self.timer.start()
    
    def stop_timer(self):
        """Detiene el timer de timeout"""
        if self.timer:
            self.timer.cancel()

# Versión simplificada para uso en API (sin interacción de usuario)
class ApiTimeoutManager:
    def __init__(self, timeout_seconds=60):
        self.timeout_seconds = timeout_seconds
        self.timeout_occurred = False
        self.timer = None
        
    def timeout_callback(self):
        """Callback que se ejecuta cuando se alcanza el timeout"""
        self.timeout_occurred = True
        print(f"⚠️ TIMEOUT: La operación ha tardado más de {self.timeout_seconds} segundos.")
        
    def start_timer(self):
        """Inicia el timer de timeout"""
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout_seconds, self.timeout_callback)
        self.timer.daemon = True
        self.timer.start()
    
    def stop_timer(self):
        """Detiene el timer de timeout"""
        if self.timer:
            self.timer.cancel()

def execute_with_timeout(func, timeout_seconds=30, *args, **kwargs):
    """
    Ejecuta una función con control de timeout interactivo (compatible con Windows)
    """
    timeout_manager = TimeoutManager(timeout_seconds)
    timeout_manager.start_timer()
    
    try:
        result = func(*args, **kwargs)
        timeout_manager.stop_timer()
        return result
    except KeyboardInterrupt:
        timeout_manager.stop_timer()
        print("\n🛑 Operación interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        timeout_manager.stop_timer()
        print(f"❌ Error durante la ejecución: {e}")
        raise

def execute_with_api_timeout(func, timeout_seconds=60, *args, **kwargs):
    """
    Ejecuta una función con control de timeout para APIs (sin interacción de usuario)
    """
    timeout_manager = ApiTimeoutManager(timeout_seconds)
    timeout_manager.start_timer()
    
    try:
        result = func(*args, **kwargs)
        timeout_manager.stop_timer()
        
        if timeout_manager.timeout_occurred:
            raise TimeoutError(f"La operación tardó más de {timeout_seconds} segundos en completarse")
        
        return result
    except Exception as e:
        timeout_manager.stop_timer()
        if timeout_manager.timeout_occurred:
            raise TimeoutError(f"La operación tardó más de {timeout_seconds} segundos y fue interrumpida")
        raise

def load_secuential_data(path):
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    df['log_ret'] = np.log(df['Adj Close']).diff()
    return df

def generate_daily_signal_secuencial(df):
    df = df.copy()
    df['variance'] = df['log_ret'].rolling(180).var()
    df = df['2020-01-01':].copy()

    ventanas = [df['log_ret'].iloc[i-180:i] for i in range(180, len(df)+1)]
    results = []
    for ventana in ventanas:
        model = arch_model(y=ventana, p=1, q=3)
        fitted = model.fit(update_freq=5, disp='off')
        results.append(fitted.forecast(horizon=1).variance.iloc[-1, 0])

    df.loc[df.index[179:], 'predictions'] = results
    df['prediction_premium'] = (df['predictions'] - df['variance']) / df['variance']
    df['premium_std'] = df['prediction_premium'].rolling(180).std()
    df['signal_daily'] = df.apply(
        lambda x: 1 if x['prediction_premium'] > 1.5 * x['premium_std'] else 
                  (-1 if x['prediction_premium'] < -1.5 * x['premium_std'] else np.nan), axis=1)
    df['signal_daily'] = df['signal_daily'].shift()
    return df

def generate_signal_intradia_secuencial(intraday_df, senales_diarias):
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

    def combination(row):
        if row['signal_daily'] == 1 and row['signal_intraday'] == 1:
            return -1
        elif row['signal_daily'] == -1 and row['signal_intraday'] == -1:
            return 1
        else:
            return np.nan

    df['return_sign'] = df.apply(combination, axis=1)
    df['return_sign'] = df.groupby(pd.Grouper(freq='D'))['return_sign'].transform(lambda x: x.ffill())
    return df

def calculate_final_return_secuencial(df):
    df = df.copy()
    df['return'] = df['close'].pct_change()
    df['forward_return'] = df['return'].shift(-1)
    df['strategy_return'] = df['forward_return'] * df['return_sign']
    df['strategy_return'] = df['strategy_return'].fillna(0)
    df['cumulative_strategy_return'] = np.exp(np.log1p(df['strategy_return']).cumsum()) - 1
    return df

# Benchmarking

def run_pipeline_sequential(path_diarios, path_intraday):
    df_diarios = load_secuential_data(path_diarios)
    df_intraday = load_intraday_data(path_intraday)
    df_senales_diarias = generate_daily_signal_secuencial(df_diarios)
    df_senales_intraday = generate_signal_intradia_secuencial(df_intraday, df_senales_diarias)
    df_retorno = calculate_final_return_secuencial(df_senales_intraday)
    
    return df_retorno

def benchmark_sequential(path_diarios, path_intraday):
    print("Midiendo el uso de CPU antes de la ejecución (sec) ...")
    cpu_before = measure_cpu_usage()  
    print(f"Uso de CPU antes: {cpu_before:.2f}%")
    
    start_time = time.time()
    result_secuencial = run_pipeline_sequential(path_diarios, path_intraday)
    secuencial_time = time.time() - start_time
    
    print("Midiendo el uso de CPU después de la ejecución (sec) ...")
    cpu_after = measure_cpu_usage()
    print(f"Uso de CPU después: {cpu_after:.2f}%")
    
    print(f"Tiempo de ejecución secuencial: {secuencial_time:.2f} segundos")
    print(f"Diferencia en el uso de CPU: {cpu_after - cpu_before:.2f}%")
    
    return result_secuencial, secuencial_time, cpu_after

def run_parallel_pipeline(path_diarios, path_intraday):
    ray.init(ignore_reinit_error=True)
    
    df_diarios = load_daily_data(path_diarios)  
    df_intraday = load_intraday_data(path_intraday)
    df_senales_diarias = generate_daily_signal(df_diarios)
    df_senales_intraday = generate_signal_intradia(df_intraday, df_senales_diarias)
    df_retorno = calculate_final_return(df_senales_intraday)
    
    return df_retorno

def benchmark_parallel(path_diarios, path_intraday):
    print("Midiendo el uso de CPU antes de la ejecución (par) ...")
    cpu_before = measure_cpu_usage() 
    print(f"Uso de CPU antes: {cpu_before:.2f}%")
    
    start_time = time.time()
    result_paralelo = run_parallel_pipeline(path_diarios, path_intraday)
    paralelo_time = time.time() - start_time
    
    print("Midiendo el uso de CPU después de la ejecución (par) ...")
    cpu_after = measure_cpu_usage()  
    print(f"Uso de CPU después: {cpu_after:.2f}%")
    
    print(f"Tiempo de ejecución paralelo: {paralelo_time:.2f} segundos")
    print(f"Diferencia en el uso de CPU: {cpu_after - cpu_before:.2f}%")
    
    return result_paralelo, paralelo_time, cpu_after

# Funciones wrapper con control de timeout
def benchmark_sequential_with_timeout(path_diarios, path_intraday, timeout=30):
    """
    Ejecuta el benchmark secuencial con control de timeout
    """
    print(f"🚀 Iniciando benchmark secuencial (timeout: {timeout}s)...")
    return execute_with_timeout(benchmark_sequential, timeout, path_diarios, path_intraday)

def benchmark_parallel_with_timeout(path_diarios, path_intraday, timeout=30):
    """
    Ejecuta el benchmark paralelo con control de timeout
    """
    print(f"🚀 Iniciando benchmark paralelo (timeout: {timeout}s)...")
    return execute_with_timeout(benchmark_parallel, timeout, path_diarios, path_intraday)

# Funciones específicas para uso en API (sin interacción de usuario)
def benchmark_sequential_for_api(path_diarios, path_intraday, timeout=120):
    """
    Ejecuta el benchmark secuencial con control de timeout para API
    """
    print(f"🚀 Iniciando benchmark secuencial para API (timeout: {timeout}s)...")
    return execute_with_api_timeout(benchmark_sequential, timeout, path_diarios, path_intraday)

def benchmark_parallel_for_api(path_diarios, path_intraday, timeout=120):
    """
    Ejecuta el benchmark paralelo con control de timeout para API
    """
    print(f"🚀 Iniciando benchmark paralelo para API (timeout: {timeout}s)...")
    return execute_with_api_timeout(benchmark_parallel, timeout, path_diarios, path_intraday)

# Ejecutar y comparar
if __name__ == "__main__":
    # Configuración de timeout (en segundos)
    TIMEOUT_SECONDS = 30
    
    print("=" * 60)
    print("🔄 INICIANDO BENCHMARKING DE ESTRATEGIA INTRADIA")
    print("=" * 60)
    print(f"⏱️  Timeout configurado: {TIMEOUT_SECONDS} segundos")
    print(f"📊 Se ejecutarán ambos pipelines (secuencial y paralelo)")
    print("=" * 60)
    
    path_diarios = "datasets/simulated_daily_data.csv"
    path_intraday = "datasets/simulated_5min_data.csv"
    
    try:
        # Benchmarking secuencial
        print("\n📈 EJECUTANDO BENCHMARK SECUENCIAL...")
        result_secuencial, secuencial_time, cpu_secuencial = benchmark_sequential_with_timeout(
            path_diarios, path_intraday, timeout=TIMEOUT_SECONDS
        )

        # Benchmarking paralelo
        print("\n🚀 EJECUTANDO BENCHMARK PARALELO...")
        result_paralelo, paralelo_time, cpu_paralelo = benchmark_parallel_with_timeout(
            path_diarios, path_intraday, timeout=TIMEOUT_SECONDS
        )

        # Comparar resultados
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE COMPARACIÓN:")
        print("=" * 60)
        print(f"⏱️  Tiempo secuencial: {secuencial_time:.2f} segundos")
        print(f"💻 Uso de CPU secuencial: {cpu_secuencial:.2f}%")
        print(f"⏱️  Tiempo paralelo: {paralelo_time:.2f} segundos")
        print(f"💻 Uso de CPU paralelo: {cpu_paralelo:.2f}%")
        
        # Calcular mejoras
        speed_improvement = ((secuencial_time - paralelo_time) / secuencial_time) * 100
        print(f"🚀 Mejora de velocidad: {speed_improvement:.1f}%")
        
        if speed_improvement > 0:
            print(f"✅ El pipeline paralelo es {speed_improvement:.1f}% más rápido")
        else:
            print(f"⚠️  El pipeline secuencial fue {abs(speed_improvement):.1f}% más rápido")

        # Crear gráfico comparativo mejorado
        print("\n📈 Generando gráficos comparativos...")
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Gráfico de tiempos de ejecución
        bars = ax1.bar(["Secuencial", "Paralelo"], [secuencial_time, paralelo_time], 
                      color=['skyblue', 'lightgreen'], alpha=0.7, 
                      label="Tiempo de Ejecución", width=0.4, align='center')
        ax1.set_ylabel("Tiempo (segundos)", color='blue', fontsize=12)
        ax1.set_xlabel("Método", fontsize=12)
        ax1.tick_params(axis='y', labelcolor='blue')

        # Agregar valores en las barras
        for bar, tiempo in zip(bars, [secuencial_time, paralelo_time]):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{tiempo:.2f}s', ha='center', va='bottom', fontweight='bold')

        # Eje secundario para el uso de CPU
        ax2 = ax1.twinx()
        line = ax2.plot(["Secuencial", "Paralelo"], [cpu_secuencial, cpu_paralelo], 
                       color='red', marker='o', label="Uso de CPU (%)", linewidth=3, markersize=8)
        ax2.set_ylabel("Uso de CPU (%)", color='red', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='red')

        # Agregar valores en los puntos
        for x, cpu_val in enumerate([cpu_secuencial, cpu_paralelo]):
            ax2.text(x, cpu_val + 1, f'{cpu_val:.1f}%', ha='center', va='bottom', 
                    color='red', fontweight='bold')

        plt.title("Comparación de Rendimiento Estrategia Intradia: Secuencial vs Paralelo", 
                 fontsize=14, fontweight='bold')
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        
        plt.tight_layout()
        plt.grid(True, alpha=0.3)

        print("✅ Mostrando gráficos...")
        plt.show()
        
        print("\n🎉 ¡Benchmarking completado exitosamente!")
        
    except KeyboardInterrupt:
        print("\n🛑 Benchmarking interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el benchmarking: {e}")
        sys.exit(1)
