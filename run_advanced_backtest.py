# run_advanced_backtest.py

import json
import pandas as pd
from pathlib import Path
from advanced_backtest import simulate_strategy_advanced

# === Load config ===
with open("config.json") as f:
    config = json.load(f)

symbol = config["symbol"]
file_name = f"{symbol}_5Min_strategy_2d.csv"

# === Load price data ===
df = pd.read_csv(file_name, parse_dates=['timestamp'], index_col='timestamp')

# === Run backtest ===
trades, equity = simulate_strategy_advanced(
    df,
    strategy=config.get("strategy_code", "sma_ema"),
    initial_capital=config["capital"],
    stop_loss_pct=config["stop_loss_pct"],
    take_profit_pct=config["take_profit_pct"],
    max_leverage=config["max_leverage"],
    symbol=symbol
)

# === Prepare output folder ===
outdir = Path(symbol)
outdir.mkdir(exist_ok=True)

# === Save results ===
trades.to_csv(outdir / f"{symbol}_advanced_trade_log.csv", index=False)
equity.to_csv(outdir / f"{symbol}_advanced_equity_curve.csv", index=False)

# === Print confirmation ===
print(f"\n📊 Trade Log for {symbol} (sample):")
print(trades.head())
print("\n📈 Final Equity:")
print(equity.tail(1))
print(f"\n💾 Saved to: {outdir}/")
