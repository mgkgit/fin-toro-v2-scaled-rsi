# visual_report.py
# Author: Monte Krull
# Creates full visual summary of SPY strategy performance

import pandas as pd
import matplotlib.pyplot as plt
from backtest_scaling import (
    apply_indicators,
    simulate_strategy,
    load_price_data,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_trade_stats
)

def plot_price_with_trades(df, trades, symbol):
    df['sma_20'] = df['close'].rolling(20).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

    plt.figure(figsize=(14, 7))
    plt.plot(df['close'], label='Close Price', linewidth=1.5)
    plt.plot(df['sma_20'], label='SMA 20', linestyle='--')
    plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

    for _, row in trades.iterrows():
        time = row['exit_time']
        if time in df.index:
            price = df.loc[time, 'close']
            color = 'green' if row['pnl'] > 0 else 'red'
            plt.scatter(time, price, color=color, marker='^' if row['pnl'] > 0 else 'v', s=100)

    plt.title(f"{symbol} Price & Trade Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    filename = f"{symbol}_trade_chart.png"
    plt.tight_layout()
    plt.savefig(filename)
    print(f"✅ Saved price chart: {filename}")
    plt.close()

def plot_equity_curve(equity, symbol):
    equity['cum_max'] = equity['equity'].cummax()
    equity['drawdown'] = equity['equity'] / equity['cum_max'] - 1

    plt.figure(figsize=(12, 6))
    plt.plot(equity['timestamp'], equity['equity'], label='Equity Curve')
    plt.fill_between(equity['timestamp'], equity['equity'], equity['cum_max'], color='red', alpha=0.2, label='Drawdown')
    plt.title(f"{symbol} Equity Curve & Drawdown")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.legend()
    plt.grid(True)
    filename = f"{symbol}_equity_curve.png"
    plt.tight_layout()
    plt.savefig(filename)
    print(f"✅ Saved equity chart: {filename}")
    plt.close()

def generate_html_report(symbol, trades, equity, stats):
    html = f"""
    <html>
    <head><title>{symbol} Strategy Report</title></head>
    <body>
        <h1>{symbol} Strategy Summary</h1>
        <ul>
            <li><b>Final Equity:</b> ${stats['final_equity']:.2f}</li>
            <li><b>Total Return:</b> {stats['total_return']:.2f}%</li>
            <li><b>Max Drawdown:</b> {stats['max_drawdown']:.2f}%</li>
            <li><b>Sharpe Ratio:</b> {stats['sharpe']}</li>
            <li><b>Win Rate:</b> {stats['win_rate']}%</li>
            <li><b>Avg Win:</b> ${stats['avg_win']}</li>
            <li><b>Avg Loss:</b> ${stats['avg_loss']}</li>
        </ul>

        <h2>📈 Price Chart with Trades</h2>
        <img src="{symbol}_trade_chart.png" width="800">

        <h2>📉 Equity Curve</h2>
        <img src="{symbol}_equity_curve.png" width="800">

        <h2>📋 Trade Log</h2>
        {trades.to_html(index=False)}
    </body>
    </html>
    """

    filename = f"{symbol}_report.html"
    with open(filename, 'w') as f:
        f.write(html)
    print(f"✅ Generated HTML report: {filename}")

if __name__ == "__main__":
    symbol = "SPY"
    file_path = f"{symbol}_5Min_strategy_2d.csv"

    # Run full backtest (not from trade log — fresh)
    raw_df = load_price_data(file_path)
    df = apply_indicators(raw_df)
    trades, equity = simulate_strategy(df)

    final_equity = equity.iloc[-1]['equity']
    total_return = (final_equity - 100000) / 100000 * 100
    max_dd = calculate_max_drawdown(equity) * 100
    sharpe = calculate_sharpe_ratio(equity)
    win_rate, avg_win, avg_loss = calculate_trade_stats(trades)

    stats = {
        "final_equity": final_equity,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }

    plot_price_with_trades(df, trades, symbol)
    plot_equity_curve(equity, symbol)
    generate_html_report(symbol, trades, equity, stats)

