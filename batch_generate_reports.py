import os
import json
import shutil
import pandas as pd
from datetime import datetime
from weasyprint import HTML
from strategy_engine import apply_indicators
from advanced_backtest import simulate_strategy_advanced
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# === Configuration List ===
configs = [
    {
        "symbol": "SPY",
        "strategy": "SMA/EMA Crossover",
        "indicators": {"sma": 20, "ema": 20},
        "capital": 100000,
        "stop_loss_pct": 0.002,
        "take_profit_pct": 0.004,
        "scaling": True,
        "max_leverage": 4,
        "repo_link": "https://github.com/mgkgit/fin-toro-v2-scaled-rsi"
    },
    {
        "symbol": "UPRO",
        "strategy": "SMA/EMA Crossover",
        "indicators": {"sma": 20, "ema": 20},
        "capital": 100000,
        "stop_loss_pct": 0.002,
        "take_profit_pct": 0.004,
        "scaling": True,
        "max_leverage": 4,
        "repo_link": "https://github.com/mgkgit/fin-toro-v2-scaled-rsi"
    }
]

summary = []

for config in configs:
    symbol = config["symbol"]
    print(f"➡️ Processing {symbol}...")

    df = pd.read_csv(f"{symbol}_5Min_strategy_2d.csv", parse_dates=['timestamp'], index_col='timestamp')
    df = apply_indicators(df, strategy="sma_ema")

    trades, equity = simulate_strategy_advanced(
        df,
        strategy="sma_ema",
        initial_capital=config["capital"],
        stop_loss_pct=config["stop_loss_pct"],
        take_profit_pct=config["take_profit_pct"],
        max_leverage=config["max_leverage"]
    )

    trades.to_csv(f"{symbol}_advanced_trade_log.csv", index=False)
    equity.to_csv(f"{symbol}_advanced_equity_curve.csv", index=False)

    # Charts
    plt.figure(figsize=(12, 6))
    plt.plot(equity['timestamp'], equity['equity'], label='Equity', linewidth=2)
    plt.title(f"{symbol} – Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{symbol}_advanced_equity_chart.png")
    plt.close()

    plt.figure(figsize=(12, 4))
    plt.plot(equity['timestamp'], equity['drawdown'], label='Drawdown', color='red')
    plt.fill_between(equity['timestamp'], equity['drawdown'], 0, color='red', alpha=0.3)
    plt.title(f"{symbol} – Drawdown")
    plt.xlabel("Time")
    plt.ylabel("Drawdown %")
    plt.tight_layout()
    plt.savefig(f"{symbol}_advanced_drawdown_chart.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    trades['pnl'].hist(bins=20, edgecolor='black')
    plt.title(f"{symbol} – PnL Distribution")
    plt.xlabel("PnL ($)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{symbol}_advanced_pnl_histogram.png")
    plt.close()

    # Metrics
    total_trades = len(trades)
    win_trades = trades[trades['pnl'] > 0]
    win_rate = (len(win_trades) / total_trades) * 100 if total_trades else 0
    avg_pnl = trades['pnl'].mean() if total_trades else 0
    max_drawdown = equity['drawdown'].min() * 100
    final_equity = equity.iloc[-1]['equity']

    equity['returns'] = equity['equity'].pct_change()
    sharpe = np.mean(equity['returns']) / np.std(equity['returns']) * np.sqrt(252*78) if np.std(equity['returns']) else 0
    volatility = np.std(equity['returns']) * np.sqrt(252*78)

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    # HTML Summary
    html = f'''
    <html>
    <head><meta charset='UTF-8'><title>{symbol} Report</title></head>
    <body>
    <h1>{symbol} Strategy Report</h1>
    <p><b>Generated:</b> {timestamp}</p>
    <ul>
        <li><b>Strategy:</b> {config['strategy']}</li>
        <li><b>Indicators:</b> SMA ({config['indicators']['sma']}), EMA ({config['indicators']['ema']})</li>
        <li><b>Capital:</b> ${config['capital']}</li>
        <li><b>Stop Loss:</b> {config['stop_loss_pct']*100:.2f}%</li>
        <li><b>Take Profit:</b> {config['take_profit_pct']*100:.2f}%</li>
        <li><b>Max Leverage:</b> {config['max_leverage']}x</li>
    </ul>
    <table border='1' cellpadding='8' cellspacing='0'>
        <tr><th>Total Trades</th><td>{total_trades}</td></tr>
        <tr><th>Win Rate (%)</th><td>{win_rate:.2f}</td></tr>
        <tr><th>Average PnL ($)</th><td>{avg_pnl:.2f}</td></tr>
        <tr><th>Max Drawdown (%)</th><td>{max_drawdown:.2f}</td></tr>
        <tr><th>Final Equity ($)</th><td>{final_equity:.2f}</td></tr>
        <tr><th>Sharpe Ratio</th><td>{sharpe:.2f}</td></tr>
        <tr><th>Volatility</th><td>{volatility:.4f}</td></tr>
    </table>
    <img src='{symbol}_advanced_equity_chart.png'><br>
    <img src='{symbol}_advanced_drawdown_chart.png'><br>
    <img src='{symbol}_advanced_pnl_histogram.png'><br>
    </body></html>
    '''

    html_path = f"{symbol}_advanced_report.html"
    with open(html_path, "w") as f:
        f.write(html)

    HTML(html_path).write_pdf(f"{symbol}_advanced_report.pdf")

    folder = Path(symbol)
    folder.mkdir(exist_ok=True)
    for suffix in ["_advanced_trade_log.csv", "_advanced_equity_curve.csv", "_advanced_equity_chart.png",
                   "_advanced_drawdown_chart.png", "_advanced_pnl_histogram.png",
                   "_advanced_report.html", "_advanced_report.pdf"]:
        shutil.move(f"{symbol}{suffix}", folder / f"{symbol}{suffix}")

    summary.append((symbol, total_trades, win_rate, avg_pnl, max_drawdown, final_equity, sharpe))

# Build index
index = '''
<html><head><title>Strategy Summary</title></head><body>
<h1>Fin-Toro V2 Strategy Summary</h1>
<table border='1' cellpadding='6' cellspacing='0'>
<tr><th>Symbol</th><th>Trades</th><th>Win %</th><th>Avg PnL</th><th>Max DD%</th><th>Final Equity</th><th>Sharpe</th><th>Report</th></tr>
'''

for s in summary:
    index += f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]:.2f}</td><td>{s[3]:.2f}</td><td>{s[4]:.2f}</td><td>{s[5]:.2f}</td><td>{s[6]:.2f}</td><td><a href='{s[0]}/{s[0]}_advanced_report.html'>View</a></td></tr>"

index += "</table><p><i>Generated by Fin-Toro V2</i></p></body></html>"
Path("index.html").write_text(index.strip())
print("✅ All complete and index.html updated.")