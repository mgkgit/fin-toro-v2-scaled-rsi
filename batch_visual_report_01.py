# batch_visual_report.py
# Author: Monte Krull
# Generates visual reports and analytics for multiple strategy CSVs

import os
import pandas as pd
from backtest_scaling import (
    apply_indicators,
    simulate_strategy,
    load_price_data,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_trade_stats
)
from visual_report import (
    plot_price_with_trades,
    plot_equity_curve,
    generate_html_report
)

def process_symbol(symbol, timeframe='5Min', days='2'):
    strategy_file = f"{symbol}_{timeframe}_strategy_{days}d.csv"
    if not os.path.exists(strategy_file):
        print(f"❌ File not found: {strategy_file}")
        return

    print(f"\n🚀 Processing: {symbol}")

    # Load and run backtest
    df = apply_indicators(load_price_data(strategy_file))
    trades, equity = simulate_strategy(df)

    final_equity = equity.iloc[-1]['equity']
    total_return = (final_equity - 100000) / 100000 * 100
    max_dd = calculate_max_drawdown(equity) * 100
    sharpe = calculate_sharpe_ratio(equity)
    win_rate, avg_win, avg_loss = calculate_trade_stats(trades)

    stats = {
        "final_equity": final_equity,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }

    # Save trade log
    trades.to_csv(f"{symbol}_strategy_trades.csv", index=False)
    print(f"💾 Saved: {symbol}_strategy_trades.csv")

    # Generate visuals + report
    plot_price_with_trades(df, trades, symbol)
    plot_equity_curve(equity, symbol)
    generate_html_report(symbol, trades, equity, stats)

def batch_process(symbols):
    for symbol in symbols:
        process_symbol(symbol)

if __name__ == "__main__":
    symbols = ["SPY", "SSO", "UPRO"]
    batch_process(symbols)
