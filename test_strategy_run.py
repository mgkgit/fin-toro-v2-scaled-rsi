import pandas as pd
from strategy_engine import apply_indicators
from backtest_scaling import simulate_strategy, calculate_max_drawdown

df = pd.read_csv("SPY_5Min_strategy_2d.csv", parse_dates=['timestamp'], index_col='timestamp')
df = apply_indicators(df, strategy="sma_ema")

trades, equity = simulate_strategy(df)

print("\n📊 Sample Trades:")
print(trades.head())

print("\n📉 Max Drawdown:")
print(f"{calculate_max_drawdown(equity)*100:.2f}%")

print("\n📈 Final Equity:")
print(equity.tail(1))
