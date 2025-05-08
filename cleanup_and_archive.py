# cleanup_and_archive.py
import os
import shutil
import pandas as pd
from datetime import datetime
from pathlib import Path

today = datetime.today().strftime("%Y-%m-%d")
archive_path = Path("archive") / today
archive_path.mkdir(parents=True, exist_ok=True)

summary = []

for item in os.listdir("."):
    symbol_path = Path(item)
    if symbol_path.is_dir() and (symbol_path / f"{item}_advanced_report.html").exists():
        print(f"📦 Archiving {item}...")

        # Read basic data for summary
        try:
            trades = pd.read_csv(symbol_path / f"{item}_advanced_trade_log.csv")
            equity = pd.read_csv(symbol_path / f"{item}_advanced_equity_curve.csv")
            total_trades = len(trades)
            win_rate = (trades['pnl'] > 0).mean() * 100
            avg_pnl = trades['pnl'].mean()
            max_dd = equity['drawdown'].min() * 100
            final_eq = equity.iloc[-1]['equity']
        except Exception as e:
            print(f"⚠️ Failed reading data from {item}: {e}")
            continue

        summary.append({
            "Symbol": item,
            "Total Trades": total_trades,
            "Win Rate (%)": round(win_rate, 2),
            "Average PnL": round(avg_pnl, 2),
            "Max Drawdown (%)": round(max_dd, 2),
            "Final Equity": round(final_eq, 2),
        })

        shutil.move(str(symbol_path), archive_path / item)

if summary:
    df = pd.DataFrame(summary)
    df.to_csv(archive_path / "report_summary.csv", index=False)
    print(f"✅ Summary written to {archive_path}/report_summary.csv")
else:
    print("ℹ️ No folders moved. Nothing to archive.")
