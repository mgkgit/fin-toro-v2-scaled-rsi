# advanced_backtest.py

import pandas as pd
from strategy_engine import apply_indicators


class DynamicPosition:
    def __init__(self, entry_price, size, leverage, entry_time):
        self.history = [(entry_price, size, leverage)]
        self.entry_time = entry_time
        self.max_price = entry_price
        self.min_price = entry_price
        self.closed = False

    def add(self, price, size, leverage):
        self.history.append((price, size, leverage))
        self.max_price = max(self.max_price, price)
        self.min_price = min(self.min_price, price)

    def update_extremes(self, price):
        self.max_price = max(self.max_price, price)
        self.min_price = min(self.min_price, price)

    def exit_position(self, exit_price):
        total_pnl = sum((exit_price - entry_price) * size * leverage for entry_price, size, leverage in self.history)
        total_size = sum(size * leverage for _, size, leverage in self.history)
        avg_leverage = sum(leverage for _, _, leverage in self.history) / len(self.history)
        return total_pnl, total_size, avg_leverage


def simulate_strategy_advanced(df, strategy="sma_ema", initial_capital=100000,
                                stop_loss_pct=0.002, take_profit_pct=0.004,
                                max_leverage=4, symbol=""):
    if symbol:
        print(f"\n🔍 Running advanced backtest for: {symbol}")

    df = apply_indicators(df, strategy=strategy)
    capital = initial_capital
    position = None
    trade_log = []
    equity_curve = []

    for i in range(len(df)):
        row = df.iloc[i]
        time = row.name
        price = row['close']
        signal = row['signal']

        if position:
            position.update_extremes(price)
            entry_price = position.history[0][0]

            if price <= entry_price * (1 - stop_loss_pct) or price >= entry_price * (1 + take_profit_pct):
                pnl, size, avg_leverage = position.exit_position(price)
                capital += pnl
                trade_log.append({
                    "entry_time": position.entry_time,
                    "exit_time": time,
                    "pnl": pnl,
                    "entry_count": len(position.history),
                    "avg_leverage": avg_leverage
                })
                print(f"❌ Exit @ {price:.2f} | PnL: ${pnl:.2f}")
                position = None

        if signal == 1 and not position:
            bet_risk = 0.01 + (0.01 * (i % 5))
            bet_amount = capital * bet_risk
            size = bet_amount / price
            leverage = min(1 + (i % max_leverage), max_leverage)
            position = DynamicPosition(price, size, leverage, entry_time=time)
            print(f"📈 Enter Long @ {price:.2f} | Size: {size:.2f} | Leverage: {leverage}x")

        elif signal == 1 and position and len(position.history) == 1:
            bet_amount = capital * 0.01
            size = bet_amount / price
            leverage = min(3, max_leverage)
            position.add(price, size, leverage)
            print(f"➕ Scaled In @ {price:.2f} (Leverage {leverage}x)")

        equity_curve.append({
            "timestamp": time,
            "equity": capital
        })

    if position:
        final_price = df.iloc[-1]['close']
        pnl, size, avg_leverage = position.exit_position(final_price)
        capital += pnl
        trade_log.append({
            "entry_time": position.entry_time,
            "exit_time": df.iloc[-1].name,
            "pnl": pnl,
            "entry_count": len(position.history),
            "avg_leverage": avg_leverage
        })
        print(f"⏹️ Forced Exit @ {final_price:.2f} | PnL: ${pnl:.2f}")

    equity_df = pd.DataFrame(equity_curve)
    trade_df = pd.DataFrame(trade_log)
    equity_df["cum_max"] = equity_df["equity"].cummax()
    equity_df["drawdown"] = equity_df["equity"] / equity_df["cum_max"] - 1

    return trade_df, equity_df
