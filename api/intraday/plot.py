import matplotlib
matplotlib.use("Agg")  # evitar errores por backend gráfico en servidores

import matplotlib.pyplot as plt
import os

def generate_plot(df, output_path="output/estrategia_plot.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(df["datetime"], df["cumulative_strategy_return"], label="Estrategia Intradía", linewidth=2, color="blue")
    plt.title("Retorno Acumulado - Estrategia Intradía")
    plt.xlabel("Fecha")
    plt.ylabel("Retorno acumulado")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.savefig(output_path)
    plt.close()
    return output_path
