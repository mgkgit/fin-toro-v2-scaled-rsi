# compare_leverage_strategies.py
# Author: Monte Krull
# Purpose: Backtest SPY, SSO, UPRO strategies with full PnL metrics and visual comparison

import os
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

def run_and_compare(symbol_files):
    results = []
    equity_curves = []

    for symbol, file in symbol_files.items():
        print(f"\n🚀 Running backtest for {symbol}...")
        df = apply_indicators(load_price_data(file))
        trades, equity = simulate_strategy(df)
        # === Save trade log for this symbol ===
        trades.to_csv(f"{symbol}_strategy_trades.csv", index=False)
        print(f"💾 Saved trade log: {symbol}_strategy_trades.csv")
        final_equity = equity.iloc[-1]['equity']
        total_return = (final_equity - 100000) / 100000
        max_dd = calculate_max_drawdown(equity)
        sharpe = calculate_sharpe_ratio(equity)
        win_rate, avg_win, avg_loss = calculate_trade_stats(trades)

        results.append({
            'Symbol': symbol,
            'Final Equity': round(final_equity, 2),
            'Total Return %': round(total_return * 100, 2),
            'Max Drawdown %': round(max_dd * 100, 2),
            'Sharpe Ratio': sharpe,
            'Win Rate %': win_rate,
            'Avg Win': avg_win,
            'Avg Loss': avg_loss
        })

        equity['symbol'] = symbol
        equity_curves.append(equity)

    return pd.DataFrame(results), pd.concat(equity_curves)

def plot_all_equity_curves(equity_df):
    plt.figure(figsize=(12, 6))
    for symbol in equity_df['symbol'].unique():
        symbol_df = equity_df[equity_df['symbol'] == symbol]
        plt.plot(symbol_df['timestamp'], symbol_df['equity'], label=symbol)

    plt.title("Equity Curve Comparison")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # File mapping
    symbol_files = {
        "SPY": "SPY_5Min_strategy_2d.csv",
        "SSO": "SSO_5Min_strategy_2d.csv",
        "UPRO": "UPRO_5Min_strategy_2d.csv"
    }

    comparison_df, equity_df = run_and_compare(symbol_files)

    print("\n📊 Strategy Performance Comparison:")
    print(comparison_df.to_string(index=False))

    plot_all_equity_curves(equity_df)
