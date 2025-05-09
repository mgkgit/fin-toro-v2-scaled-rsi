from pathlib import Path
from datetime import datetime
import os
import shutil
import json
import pandas as pd
import matplotlib.pyplot as plt
from weasyprint import HTML
from strategy_engine import apply_indicators
from advanced_backtest import simulate_strategy_advanced

# === Strategy Configurations ===
configs = [
    {
        "symbol": "SPY",
        "strategy": "sma_ema",
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
        "strategy": "macd",
        "indicators": {"fast": 12, "slow": 26, "signal": 9},
        "capital": 100000,
        "stop_loss_pct": 0.002,
        "take_profit_pct": 0.004,
        "scaling": True,
        "max_leverage": 4,
        "repo_link": "https://github.com/mgkgit/fin-toro-v2-scaled-rsi"
    },
    {
        "symbol": "SPY",
        "strategy": "bollinger",
        "indicators": {"sma": 20, "stddev": 2},
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
    strategy = config["strategy"]
    tag = f"{symbol}_{strategy}"
    print(f"➡️ Processing {tag}...")

    df = pd.read_csv(f"{symbol}_5Min_strategy_2d.csv", parse_dates=['timestamp'], index_col='timestamp')
    df = apply_indicators(df, strategy=strategy, **config["indicators"])

    trades, equity = simulate_strategy_advanced(
        df,
        strategy=strategy,
        initial_capital=config["capital"],
        stop_loss_pct=config["stop_loss_pct"],
        take_profit_pct=config["take_profit_pct"],
        max_leverage=config["max_leverage"]
    )

    trades.to_csv(f"{tag}_trade_log.csv", index=False)
    equity.to_csv(f"{tag}_equity_curve.csv", index=False)

    # === Charts ===
    plt.figure(figsize=(12, 6))
    plt.plot(equity['timestamp'], equity['equity'], label='Equity', linewidth=2)
    plt.title("📈 Advanced Backtest – Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{tag}_equity_chart.png")
    plt.close()

    plt.figure(figsize=(12, 4))
    plt.plot(equity['timestamp'], equity['drawdown'], label='Drawdown', color='red')
    plt.fill_between(equity['timestamp'], equity['drawdown'], 0, color='red', alpha=0.3)
    plt.title("📉 Drawdown Over Time")
    plt.xlabel("Time")
    plt.ylabel("Drawdown %")
    plt.tight_layout()
    plt.savefig(f"{tag}_drawdown_chart.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    trades['pnl'].hist(bins=20, edgecolor='black')
    plt.title("📊 PnL Distribution")
    plt.xlabel("PnL ($)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{tag}_pnl_histogram.png")
    plt.close()

    # === Stats ===
    total_trades = len(trades)
    win_trades = trades[trades['pnl'] > 0]
    win_rate = (len(win_trades) / total_trades) * 100 if total_trades else 0
    avg_pnl = trades['pnl'].mean() if total_trades else 0
    max_drawdown = equity['drawdown'].min() * 100
    final_equity = equity.iloc[-1]['equity']
    volatility = equity['equity'].pct_change().std() * 100
    sharpe_ratio = (
        (equity['equity'].pct_change().mean() / equity['equity'].pct_change().std()) * (252**0.5)
        if equity['equity'].pct_change().std() > 0 else 0
    )

    html = f"""
    <html>
    <head><meta charset='UTF-8'><title>{tag} Report</title></head>
    <body>
    <h1>📘 {tag} Strategy Report</h1>
    <ul>
        <li><b>Strategy:</b> {config['strategy']}</li>
        <li><b>Indicators:</b> {json.dumps(config['indicators'])}</li>
        <li><b>Initial Capital:</b> ${config['capital']}</li>
        <li><b>Stop Loss:</b> {config['stop_loss_pct']*100:.2f}%</li>
        <li><b>Take Profit:</b> {config['take_profit_pct']*100:.2f}%</li>
        <li><b>Max Leverage:</b> {config['max_leverage']}x</li>
    </ul>
    <table border='1' cellpadding='8' cellspacing='0'>
        <tr><th>Total Trades</th><td>{total_trades}</td></tr>
        <tr><th>Win Rate (%)</th><td>{win_rate:.2f}</td></tr>
        <tr><th>Average PnL ($)</th><td>{avg_pnl:.2f}</td></tr>
        <tr><th>Max Drawdown (%)</th><td>{max_drawdown:.2f}</td></tr>
        <tr><th>Volatility (%)</th><td>{volatility:.2f}</td></tr>
        <tr><th>Sharpe Ratio</th><td>{sharpe_ratio:.2f}</td></tr>
        <tr><th>Final Equity ($)</th><td>{final_equity:.2f}</td></tr>
    </table>
    <img src='{tag}_equity_chart.png'><br>
    <img src='{tag}_drawdown_chart.png'><br>
    <img src='{tag}_pnl_histogram.png'><br>
    </body></html>
    """

    html_path = f"{tag}_report.html"
    with open(html_path, "w") as f:
        f.write(html)
    HTML(html_path).write_pdf(f"{tag}_report.pdf")

    out_dir = Path(tag)
    out_dir.mkdir(exist_ok=True)
    for suffix in [
        "_trade_log.csv", "_equity_curve.csv", "_report.html", "_report.pdf",
        "_equity_chart.png", "_drawdown_chart.png", "_pnl_histogram.png"
    ]:
        file = f"{tag}{suffix}"
        shutil.move(file, out_dir / file)

    summary.append((tag, total_trades, win_rate, avg_pnl, max_drawdown, final_equity, volatility, sharpe_ratio))

# === Build Index Page ===
index = """
<html>
<head><title>Fin-Toro Strategy Summary</title></head>
<body>
<h1>📘 Batch Strategy Index</h1>
<table border='1' cellpadding='8' cellspacing='0'>
<tr><th>Tag</th><th>Total Trades</th><th>Win %</th><th>Avg PnL</th><th>Max DD %</th><th>Volatility %</th><th>Sharpe</th><th>Final Equity</th><th>View</th></tr>
"""
for s in summary:
    index += f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]:.2f}</td><td>{s[3]:.2f}</td><td>{s[4]:.2f}</td><td>{s[6]:.2f}</td><td>{s[7]:.2f}</td><td>{s[5]:.2f}</td><td><a href='{s[0]}/{s[0]}_report.html'>📄</a></td></tr>"
index += "</table></body></html>"
Path("index.html").write_text(index.strip())

print("✅ All reports and index.html generated.")
