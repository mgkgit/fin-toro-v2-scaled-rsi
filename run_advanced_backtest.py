# run_advanced_backtest.py

import pandas as pd
from advanced_backtest import simulate_strategy_advanced
from strategy_engine import apply_indicators

# === Test configuration ===
config = {
    "symbol": "SPY",
    "strategy": "macd",  # Try "bollinger", "sma_ema", etc.
    "capital": 100000,
    "stop_loss_pct": 0.002,
    "take_profit_pct": 0.004,
    "max_leverage": 4
}

symbol = config["symbol"]

# === Load price data ===
df = pd.read_csv(f"{symbol}_5Min_strategy_2d.csv", parse_dates=['timestamp'], index_col='timestamp')
df = apply_indicators(df, strategy=config["strategy"])

# === Simulate strategy ===
trades, equity = simulate_strategy_advanced(
    df,
    strategy=config["strategy"],
    initial_capital=config["capital"],
    stop_loss_pct=config["stop_loss_pct"],
    take_profit_pct=config["take_profit_pct"],
    max_leverage=config["max_leverage"]
)

# === Save outputs ===
trades.to_csv(f"{symbol}_advanced_trade_log.csv", index=False)
equity.to_csv(f"{symbol}_advanced_equity_curve.csv", index=False)

print("\n📊 Sample Trades:")
print(trades.head())

print("\n📈 Final Equity:")
print(equity.tail(1))

print("\n💾 Exported:")
print(f" - {symbol}_advanced_trade_log.csv")
print(f" - {symbol}_advanced_equity_curve.csv")
