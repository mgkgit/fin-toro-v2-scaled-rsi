# batch_visual_report.py
# Author: Monte Krull
# Runs full visual + PDF reports for multiple symbols

from pathlib import Path
from weasyprint import HTML
from backtest_scaling import (
    apply_indicators,
    simulate_strategy,
    load_price_data,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_trade_stats
)
import matplotlib.pyplot as plt
import pandas as pd

def plot_price_with_trades(df, trades, symbol, folder):
    df['sma_20'] = df['close'].rolling(20).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

    plt.figure(figsize=(14, 7))
    plt.plot(df['close'], label='Close', linewidth=1.5)
    plt.plot(df['sma_20'], label='SMA 20', linestyle='--')
    plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

    for _, row in trades.iterrows():
        time = row['exit_time']
        if time in df.index:
            price = df.loc[time, 'close']
            color = 'green' if row['pnl'] > 0 else 'red'
            marker = '^' if row['pnl'] > 0 else 'v'
            plt.scatter(time, price, color=color, marker=marker, s=100)

    plt.title(f"{symbol} – Price Chart & Trades")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    filename = folder / f"{symbol}_trade_chart.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ Saved chart: {filename.name}")

def plot_equity_curve(equity, symbol, folder):
    equity['cum_max'] = equity['equity'].cummax()
    equity['drawdown'] = equity['equity'] / equity['cum_max'] - 1

    plt.figure(figsize=(12, 6))
    plt.plot(equity['timestamp'], equity['equity'], label='Equity')
    plt.fill_between(equity['timestamp'], equity['equity'], equity['cum_max'], alpha=0.2, color='red', label='Drawdown')
    plt.title(f"{symbol} – Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity ($)")
    plt.legend()
    plt.grid(True)
    filename = folder / f"{symbol}_equity_curve.png"
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ Saved curve: {filename.name}")

def generate_html_report(symbol, trades, stats, folder):
    html_path = folder / f"{symbol}_report.html"
    pdf_path = folder / f"{symbol}_report.pdf"

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial; padding: 1.5em; }}
        h1, h2 {{ color: #222; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 0.3em 0; }}
        img {{ margin: 1em 0; max-width: 100%; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 0.4em; text-align: right; }}
    </style>
    </head>
    <body>
        <h1>{symbol} Strategy Summary</h1>
        <ul>
            <li><b>Final Equity:</b> ${stats['final_equity']:.2f}</li>
            <li><b>Total Return:</b> {stats['total_return']:.2f}%</li>
            <li><b>Max Drawdown:</b> {stats['max_drawdown']:.2f}%</li>
            <li><b>Sharpe Ratio:</b> {stats['sharpe']}</li>
            <li><b>Win Rate:</b> {stats['win_rate']}%</li>
            <li><b>Avg Win:</b> ${stats['avg_win']}</li>
            <li><b>Avg Loss:</b> ${stats['avg_loss']}</li>
        </ul>
        <h2>📈 Price Chart</h2>
        <img src="{symbol}_trade_chart.png">
        <h2>📉 Equity Curve</h2>
        <img src="{symbol}_equity_curve.png">
        <h2>📋 Trade Log</h2>
        {trades.to_html(index=False)}
    </body>
    </html>
    """

    with open(html_path, "w") as f:
        f.write(html)
    print(f"✅ HTML report: {html_path.name}")

    try:
        HTML(string=html, base_url=str(folder)).write_pdf(pdf_path)
        print(f"📄 PDF report: {pdf_path.name}")
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")

def process_symbol(symbol, timeframe='5Min', days='2'):
    strategy_file = f"{symbol}_{timeframe}_strategy_{days}d.csv"
    folder = Path(f"reports/{symbol}")
    folder.mkdir(parents=True, exist_ok=True)

    try:
        df = apply_indicators(load_price_data(strategy_file))
    except Exception as e:
        print(f"❌ Could not process {symbol}: {e}")
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
    print(f"💾 Saved trade log: {symbol}_strategy_trades.csv")

    plot_price_with_trades(df, trades, symbol, folder)
    plot_equity_curve(equity, symbol, folder)
    generate_html_report(symbol, trades, stats, folder)

def run_batch(symbols):
    print("\n📊 Starting Batch Strategy Reporting...")
    for symbol in symbols:
        print(f"\n➡️ Processing {symbol}...")
        process_symbol(symbol)
    print("\n✅ All reports generated.")

if __name__ == "__main__":
    run_batch(["SPY", "SSO", "UPRO"])
