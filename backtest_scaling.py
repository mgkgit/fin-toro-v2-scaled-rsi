# backtest_scaling.py
# Author: Monte Krull
# Simulates SMA/EMA crossover strategy with scaling, leverage, equity tracking, and performance metrics

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Position:
    def __init__(self, entry_price, base_size, leverage):
        self.entry_price = entry_price
        self.size = base_size
        self.leverage = leverage
        self.scaled_steps = 0
        self.history = [(entry_price, base_size, leverage)]

    def scale_in(self, price, add_size, new_leverage):
        self.size += add_size
        self.leverage = new_leverage
        self.scaled_steps += 1
        self.history.append((price, add_size, new_leverage))

    def scale_out(self, reduce_size):
        self.size = max(self.size - reduce_size, 0)

    def exit_position(self, price):
        total_pnl = 0
        for entry_price, size, leverage in self.history:
            pnl = ((price - entry_price) * size * leverage)
            total_pnl += pnl
        return total_pnl

def apply_indicators(df):
    df['sma_20'] = df['close'].rolling(20).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['signal'] = 0
    df.loc[df['ema_20'] > df['sma_20'], 'signal'] = 1
    df.loc[df['ema_20'] < df['sma_20'], 'signal'] = -1
    return df

def simulate_strategy(df):
    position = None
    trade_log = []
    capital = 100000
    equity_curve = []

    for i in range(20, len(df)):
        row = df.iloc[i]
        price = row['close']
        signal = row['signal']
        timestamp = row.name

        if position is None:
            if signal == 1:
                base_size = capital * 0.5 / price
                position = Position(entry_price=price, base_size=base_size, leverage=2)
                print(f"📈 Enter Long @ {price:.2f}")

        else:
            last_entry_price = position.history[-1][0]

            if price >= last_entry_price * 1.005 and position.scaled_steps == 0:
                add_size = capital * 0.25 / price
                position.scale_in(price, add_size, 3)
                print(f"➕ Scaled In @ {price:.2f} (Leverage 3x)")

            elif price >= last_entry_price * 1.01 and position.scaled_steps == 1:
                add_size = capital * 0.25 / price
                position.scale_in(price, add_size, 4)
                print(f"➕ Final Scale @ {price:.2f} (Leverage 4x)")

            elif price <= last_entry_price * 0.995 and position.size > 0:
                reduce_size = position.size * 0.25
                position.scale_out(reduce_size)
                print(f"➖ Scaled Out @ {price:.2f}")

            elif signal == -1:
                pnl = position.exit_position(price)
                avg_lev = np.mean([lev for _, _, lev in position.history])
                trade_log.append({
                    'exit_time': timestamp,
                    'pnl': pnl,
                    'entry_count': len(position.history),
                    'avg_leverage': round(avg_lev, 2)
                })

                print(f"❌ Exit @ {price:.2f} | PnL: ${pnl:.2f}")
                capital += pnl
                position = None

        equity_curve.append({'timestamp': timestamp, 'equity': capital})

    return pd.DataFrame(trade_log), pd.DataFrame(equity_curve)

def load_price_data(file_path):
    df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
    return df[['close']]

def calculate_max_drawdown(equity_df):
    equity_df['cum_max'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = equity_df['equity'] / equity_df['cum_max'] - 1
    max_dd = equity_df['drawdown'].min()
    print(f"\n📉 Max Drawdown: {max_dd:.2%}")
    return max_dd

def plot_equity_curve(equity_df):
    plt.figure(figsize=(12, 5))
    plt.plot(equity_df['timestamp'], equity_df['equity'], label='Equity Curve', linewidth=2)
    plt.title("📈 Strategy Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

def calculate_sharpe_ratio(equity_df, risk_free_rate=0.01):
    equity_df['returns'] = equity_df['equity'].pct_change().fillna(0)
    excess_returns = equity_df['returns'] - (risk_free_rate / 252)
    sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    return round(sharpe, 2)

def calculate_trade_stats(trade_df):
    wins = trade_df[trade_df['pnl'] > 0]
    losses = trade_df[trade_df['pnl'] < 0]
    win_rate = len(wins) / len(trade_df) if len(trade_df) > 0 else 0
    avg_win = wins['pnl'].mean() if not wins.empty else 0
    avg_loss = losses['pnl'].mean() if not losses.empty else 0
    return round(win_rate * 100, 2), round(avg_win, 2), round(avg_loss, 2)

# === MAIN TEST BLOCK ===
if __name__ == "__main__":
    file_path = "symbol_5Min_strategy_2d.csv"  # Replace as needed
    raw_df = load_price_data(file_path)
    df = apply_indicators(raw_df)
    trades, equity = simulate_strategy(df)
    # === Export Trade Log ===
    trades.to_csv("symbol_strategy_trades.csv", index=False)
    print("💾 Trade log saved to symbol_strategy_trades.csv")

    print("\n📊 Trade Summary:")
    print(trades)

    print("\n📈 Final Equity: ${:.2f}".format(equity.iloc[-1]['equity']))
    calculate_max_drawdown(equity)
    plot_equity_curve(equity)
