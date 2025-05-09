# run_strategies_batch.py

import os
import json
import pandas as pd
from pathlib import Path
from strategy_engine import apply_indicators
from advanced_backtest import simulate_strategy_advanced
import matplotlib.pyplot as plt
from weasyprint import HTML

CONFIG_DIR = Path("configs")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def process_strategy(config_path):
    with open(config_path) as f:
        config = json.load(f)

    symbol = config["symbol"]
    print(f"\n➡️ Running strategy for {symbol}")

    # Load data
    data_file = f"{symbol}_5Min_strategy_2d.csv"
    df = pd.read_csv(data_file, parse_dates=['timestamp'], index_col='timestamp')

    # Apply indicators
    df = apply_indicators(df, strategy=config['strategy'], **config.get("indicators", {}))

    # Backtest
    trades, equity = simulate_strategy_advanced(
        df,
        strategy=config['strategy'],
        initial_capital=config['capital'],
        stop_loss_pct=config['stop_loss_pct'],
        take_profit_pct=config['take_profit_pct'],
        max_leverage=config['max_leverage']
    )

    # Output paths
    symbol_dir = OUTPUT_DIR / symbol
    symbol_dir.mkdir(exist_ok=True)

    # Save data
    trades.to_csv(symbol_dir / f"{symbol}_advanced_trade_log.csv", index=False)
    equity.to_csv(symbol_dir / f"{symbol}_advanced_equity_curve.csv", index=False)

    # Chart 1 – Equity Curve
    plt.figure(figsize=(12, 6))
    plt.plot(equity['timestamp'], equity['equity'], label='Equity')
    plt.title(f"{symbol} Equity Curve")
    plt.grid(True)
    plt.tight_layout()
    equity_chart = symbol_dir / f"{symbol}_equity_chart.png"
    plt.savefig(equity_chart)
    plt.close()

    # Chart 2 – Drawdown
    plt.figure(figsize=(12, 4))
    plt.plot(equity['timestamp'], equity['drawdown'], label='Drawdown', color='red')
    plt.fill_between(equity['timestamp'], equity['drawdown'], 0, color='red', alpha=0.3)
    plt.title(f"{symbol} Drawdown Curve")
    plt.tight_layout()
    dd_chart = symbol_dir / f"{symbol}_drawdown_chart.png"
    plt.savefig(dd_chart)
    plt.close()

    # Chart 3 – PnL Histogram
    plt.figure(figsize=(8, 5))
    trades['pnl'].hist(bins=20, edgecolor='black')
    plt.title(f"{symbol} PnL Distribution")
    plt.tight_layout()
    pnl_chart = symbol_dir / f"{symbol}_pnl_histogram.png"
    plt.savefig(pnl_chart)
    plt.close()

    # HTML Summary Report
    win_trades = trades[trades['pnl'] > 0]
    win_rate = (len(win_trades) / len(trades)) * 100 if len(trades) else 0
    avg_pnl = trades['pnl'].mean()
    max_drawdown = equity['drawdown'].min() * 100
    final_equity = equity.iloc[-1]['equity']

    html = f"""
    <html>
    <head><meta charset='UTF-8'><title>{symbol} Report</title></head>
    <body>
    <h1>📘 {symbol} Strategy Report</h1>
    <ul>
        <li><b>Strategy:</b> {config['strategy']}</li>
        <li><b>Capital:</b> ${config['capital']}</li>
        <li><b>Stop Loss:</b> {config['stop_loss_pct']*100:.2f}%</li>
        <li><b>Take Profit:</b> {config['take_profit_pct']*100:.2f}%</li>
        <li><b>Max Leverage:</b> {config['max_leverage']}x</li>
    </ul>
    <table border='1'>
        <tr><th>Total Trades</th><td>{len(trades)}</td></tr>
        <tr><th>Win Rate</th><td>{win_rate:.2f}%</td></tr>
        <tr><th>Avg PnL</th><td>${avg_pnl:.2f}</td></tr>
        <tr><th>Max Drawdown</th><td>{max_drawdown:.2f}%</td></tr>
        <tr><th>Final Equity</th><td>${final_equity:.2f}</td></tr>
    </table>
    <img src="{equity_chart.name}">
    <img src="{dd_chart.name}">
    <img src="{pnl_chart.name}">
    </body>
    </html>
    """

    html_path = symbol_dir / f"{symbol}_report.html"
    pdf_path = symbol_dir / f"{symbol}_report.pdf"
    with open(html_path, "w") as f:
        f.write(html)
    HTML(str(html_path)).write_pdf(str(pdf_path))

    print(f"✅ Report complete for {symbol}: {pdf_path.name}")

# === MAIN ===
def main():
    for file in CONFIG_DIR.glob("*.json"):
        process_strategy(file)

if __name__ == "__main__":
    main()
