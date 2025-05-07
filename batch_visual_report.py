# batch_visual_report.py
# Author: Monte Krull
# Processes strategy reports for SPY, SSO, UPRO

from visual_report import (
    plot_price_with_trades,
    plot_equity_curve,
    generate_html_report
)
from backtest_scaling import (
    apply_indicators,
    simulate_strategy,
    load_price_data,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_trade_stats
)
from pathlib import Path
import pandas as pd

def process_symbol(symbol, timeframe='5Min', days='2'):
    strategy_file = f"{symbol}_{timeframe}_strategy_{days}d.csv"
    folder = Path(f"reports/{symbol}")
    folder.mkdir(parents=True, exist_ok=True)

    try:
        df = apply_indicators(load_price_data(strategy_file))
    except Exception as e:
        print(f"❌ Failed to load {strategy_file}: {e}")
        return

    trades, equity = simulate_strategy(df)

    stats = {
        "final_equity": equity.iloc[-1]['equity'],
        "total_return": (equity.iloc[-1]['equity'] - 100000) / 100000 * 100,
        "max_drawdown": calculate_max_drawdown(equity) * 100,
        "sharpe": calculate_sharpe_ratio(equity),
        "win_rate": calculate_trade_stats(trades)[0],
        "avg_win": calculate_trade_stats(trades)[1],
        "avg_loss": calculate_trade_stats(trades)[2]
    }

    trades.to_csv(folder / f"{symbol}_strategy_trades.csv", index=False)
    plot_price_with_trades(df, trades, symbol, folder)
    plot_equity_curve(equity, symbol, folder)
    generate_html_report(symbol, trades, stats, folder)

def run_batch(symbols):
    for symbol in symbols:
        process_symbol(symbol)

if __name__ == "__main__":
    run_batch(["SPY", "SSO", "UPRO"])
