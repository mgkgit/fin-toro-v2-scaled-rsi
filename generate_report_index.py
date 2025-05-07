# generate_report_index.py
# Generates an index.html summary dashboard for all reports

from pathlib import Path
import datetime
import pandas as pd

def generate_index():
    base_path = Path("reports")
    if not base_path.exists():
        print("❌ Error: 'reports/' folder does not exist.")
        return

    html = """<html><head>
    <title>Trading Strategy Report Index</title>
    <style>
        body { font-family: Arial; padding: 2em; background: #f9f9f9; }
        h1 { margin-bottom: 1em; }
        .grid { display: flex; flex-wrap: wrap; gap: 1em; }
        .card {
            background: white;
            border-radius: 8px;
            padding: 1em;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        .symbol { font-size: 1.3em; font-weight: bold; }
        .meta, .stat { font-size: 0.9em; color: #555; margin: 0.3em 0; }
        a { text-decoration: none; color: #007acc; }
        a:hover { text-decoration: underline; }
    </style>
    </head><body>
    <h1>📊 Strategy Report Index</h1>
    <div class="grid">
    """

    for folder in sorted(base_path.iterdir()):
        if folder.is_dir():
            symbol = folder.name
            html_path = folder / f"{symbol}_report.html"
            pdf_path = folder / f"{symbol}_report.pdf"
            csv_path = folder / f"{symbol}_strategy_trades.csv"

            if not html_path.exists() or not csv_path.exists():
                continue

            timestamp = datetime.datetime.fromtimestamp(
                html_path.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M")

            try:
                trades = pd.read_csv(csv_path)
                pnl = trades['pnl']
                total_return = pnl.sum()
                win_rate = (pnl > 0).mean() * 100
                avg_win = pnl[pnl > 0].mean() if not pnl[pnl > 0].empty else 0
                avg_loss = pnl[pnl < 0].mean() if not pnl[pnl < 0].empty else 0

                stats = f"""
                <div class='stat'><b>Total PnL:</b> ${total_return:,.2f}</div>
                <div class='stat'><b>Win Rate:</b> {win_rate:.2f}%</div>
                <div class='stat'><b>Avg Win:</b> ${avg_win:,.2f}</div>
                <div class='stat'><b>Avg Loss:</b> ${avg_loss:,.2f}</div>
                """
            except Exception as e:
                stats = "<div class='stat'>⚠️ Error reading stats</div>"

            html += f"""
            <div class="card">
                <div class="symbol">{symbol}</div>
                <div class="meta">Last updated: {timestamp}</div>
                {stats}
                <div class="meta"><a href="{symbol}/{symbol}_report.html" target="_blank">🖥 View HTML Report</a></div>
                <div class="meta"><a href="{symbol}/{symbol}_report.pdf" target="_blank">📄 Download PDF Report</a></div>
                <div class="meta"><a href="{symbol}/{symbol}_strategy_trades.csv" target="_blank">📊 Trade Log CSV</a></div>
            </div>
            """

    html += "</div></body></html>"

    index_path = base_path / "index.html"
    with open(index_path, "w") as f:
        f.write(html)

    print(f"✅ Index generated: {index_path}")

if __name__ == "__main__":
    generate_index()
