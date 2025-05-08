# plot_advanced_results.py

import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# === Load config ===
with open("config.json") as f:
    config = json.load(f)

symbol = config["symbol"]
outdir = Path(symbol)

# === Load data ===
trades = pd.read_csv(outdir / f"{symbol}_advanced_trade_log.csv", parse_dates=['entry_time', 'exit_time'])
equity = pd.read_csv(outdir / f"{symbol}_advanced_equity_curve.csv", parse_dates=['timestamp'])

# === Plot equity curve ===
plt.figure(figsize=(12, 6))
plt.plot(equity['timestamp'], equity['equity'], label='Equity', linewidth=2)
plt.title(f"📈 {symbol} Advanced Backtest – Equity Curve")
plt.xlabel("Time")
plt.ylabel("Equity ($)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(outdir / f"{symbol}_advanced_equity_chart.png")
plt.close()

# === Plot drawdown ===
plt.figure(figsize=(12, 4))
plt.plot(equity['timestamp'], equity['drawdown'], label='Drawdown', color='red')
plt.fill_between(equity['timestamp'], equity['drawdown'], 0, color='red', alpha=0.3)
plt.title(f"📉 {symbol} Drawdown Over Time")
plt.xlabel("Time")
plt.ylabel("Drawdown %")
plt.tight_layout()
plt.savefig(outdir / f"{symbol}_advanced_drawdown_chart.png")
plt.close()

# === Plot PnL histogram ===
plt.figure(figsize=(8, 5))
trades['pnl'].hist(bins=20, edgecolor='black')
plt.title(f"📊 {symbol} PnL Distribution")
plt.xlabel("PnL ($)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(outdir / f"{symbol}_advanced_pnl_histogram.png")
plt.close()

print(f"✅ Charts saved in folder: {outdir}/")
