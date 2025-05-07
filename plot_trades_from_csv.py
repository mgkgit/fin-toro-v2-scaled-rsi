# plot_trades_from_csv.py
# Author: Monte Krull
# Visualizes trade entries and exits on a price chart with SMA/EMA

import pandas as pd
import matplotlib.pyplot as plt
import argparse

def plot_trades(price_file, trade_file, symbol):
    # Load data
    df = pd.read_csv(price_file, index_col='timestamp', parse_dates=True)
    trades = pd.read_csv(trade_file, parse_dates=['exit_time'])

    # Recalculate indicators for visual context
    df['sma_20'] = df['close'].rolling(20).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

    # Create plot
    plt.figure(figsize=(14, 7))
    plt.plot(df['close'], label='Close', linewidth=1.5)
    plt.plot(df['sma_20'], label='SMA 20', linestyle='--')
    plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

    # Plot trade exits (since only exits are tracked for now)
    for _, row in trades.iterrows():
        time = row['exit_time']
        if time in df.index:
            price = df.loc[time, 'close']
            color = 'green' if row['pnl'] > 0 else 'red'
            label = 'Exit (Win)' if row['pnl'] > 0 else 'Exit (Loss)'
            plt.scatter(time, price, color=color, marker='^' if row['pnl'] > 0 else 'v', s=80, label=label)

    plt.title(f"{symbol} Strategy Trade Chart")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()

    # Save chart
    filename = f"{symbol}_trade_chart.png"
    plt.savefig(filename)
    print(f"✅ Chart saved: {filename}")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot trades from CSV')
    parser.add_argument('--symbol', required=True, help='Symbol (e.g., SPY)')
    parser.add_argument('--timeframe', default='5Min', help='Timeframe used')
    parser.add_argument('--days', default='2', help='Days of history')

    args = parser.parse_args()
    symbol = args.symbol.upper()
    price_file = f"{symbol}_{args.timeframe}_strategy_{args.days}d.csv"
    trade_file = f"{symbol}_strategy_trades.csv"

    plot_trades(price_file, trade_file, symbol)
