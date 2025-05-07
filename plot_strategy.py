# plot_strategy.py
# Author: Monte Krull
# Purpose: Visualize SMA/EMA crossover strategy with matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import argparse

def plot_strategy(csv_file, symbol=None):
    # === Load Data ===
    df = pd.read_csv(csv_file, index_col='timestamp', parse_dates=True)

    # === Set up Chart ===
    plt.figure(figsize=(12, 6))
    plt.plot(df['close'], label='Close', linewidth=1.5)
    plt.plot(df['sma_20'], label='SMA 20', linestyle='--')
    plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

    # === Plot Buy/Sell Signals ===
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]

    plt.scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', label='Sell Signal')

    # === Labels and Styling ===
    title = f"{symbol or csv_file} – SMA/EMA Strategy"
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # === Save and Show Chart ===
    filename = f"{symbol}_strategy_chart.png" if symbol else "strategy_chart.png"
    plt.savefig(filename)
    print(f"📸 Chart saved to {filename}")

    plt.show()

# === CLI Entry Point ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot SMA/EMA Strategy with signals')
    parser.add_argument('--file', type=str, required=True, help='Path to strategy-enhanced CSV file')
    parser.add_argument('--symbol', type=str, help='Ticker symbol (for chart title and filename)')
    args = parser.parse_args()

    plot_strategy(args.file, args.symbol)
