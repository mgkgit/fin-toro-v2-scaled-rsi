# plot_all_strategies.py
# Author: Monte Krull
# Batch plots all strategy-enhanced CSV files in the folder

import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_strategy(csv_path):
    symbol = os.path.basename(csv_path).split('_')[0]
    df = pd.read_csv(csv_path, index_col='timestamp', parse_dates=True)

    plt.figure(figsize=(12, 6))
    plt.plot(df['close'], label='Close', linewidth=1.5)
    plt.plot(df['sma_20'], label='SMA 20', linestyle='--')
    plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

    # Plot signals
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]
    plt.scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', label='Buy')
    plt.scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', label='Sell')

    # Labels
    plt.title(f"{symbol} – SMA/EMA Strategy")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # ✅ Save chart within the same function
    filename = f"{symbol}_strategy_chart.png"
    plt.savefig(filename)
    print(f"✅ Saved: {filename}")
    plt.close()  # Prevents memory issues and overlapping plots

def batch_plot_strategies(folder='.'):
    print(f"📁 Scanning folder: {folder}")
    for file in os.listdir(folder):
        # ✅ Only match CSVs with "_strategy_" AND ".csv"
        if file.endswith('.csv') and '_strategy_' in file:
            try:
                print(f"📊 Plotting: {file}")
                plot_strategy(os.path.join(folder, file))
            except Exception as e:
                print(f"❌ Error with {file}: {e}")

if __name__ == "__main__":
    batch_plot_strategies()
