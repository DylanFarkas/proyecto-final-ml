import pandas as pd
import matplotlib.pyplot as plt

def generate_plot():
    df = pd.read_csv("output/cumulative_returns.csv", parse_dates=["Date"])
    df.set_index("Date", inplace=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df["portfolio_returns"], label="Estrategia Twitter", linewidth=2)
    plt.plot(df["nasdaq_return"], label="Nasdaq (QQQ)", linestyle="--")
    plt.title("Retornos acumulados")
    plt.xlabel("Fecha")
    plt.ylabel("Retorno acumulado")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_path = "output/returns_plot.png"
    plt.savefig(plot_path)
    plt.close()
    return plot_path
