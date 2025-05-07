# generate_report_index.py
# Creates a clickable dashboard of all strategy reports

from pathlib import Path
import datetime

def generate_index():
    base_path = Path("reports")
    html = """<html><head>
    <title>Trading Strategy Report Index</title>
    <style>
        body { font-family: Arial; padding: 2em; background: #f9f9f9; }
        h1 { margin-bottom: 1em; }
        ul { list-style: none; padding: 0; }
        li { margin: 1em 0; }
        .card {
            background: white;
            border-radius: 8px;
            padding: 1em;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-bottom: 1.5em;
        }
        .symbol { font-size: 1.3em; font-weight: bold; }
        .meta { font-size: 0.9em; color: #555; }
        a { text-decoration: none; color: #007acc; }
        a:hover { text-decoration: underline; }
    </style>
    </head><body>
    <h1>📊 Strategy Report Index</h1>
    """

    for folder in sorted(base_path.iterdir()):
        if folder.is_dir():
            symbol = folder.name
            html_path = folder / f"{symbol}_report.html"
            pdf_path = folder / f"{symbol}_report.pdf"
            csv_path = folder / f"{symbol}_strategy_trades.csv"

            last_modified = datetime.datetime.fromtimestamp(
                html_path.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M")

            html += f"""
            <div class="card">
                <div class="symbol">{symbol}</div>
                <div class="meta">Last updated: {last_modified}</div>
                <ul>
                    <li>🖥 <a href="{symbol}/{symbol}_report.html" target="_blank">View HTML Report</a></li>
                    <li>📄 <a href="{symbol}/{symbol}_report.pdf" target="_blank">Download PDF Report</a></li>
                    <li>📊 <a href="{symbol}/{symbol}_strategy_trades.csv" target="_blank">Trade Log CSV</a></li>
                </ul>
            </div>
            """

    html += "</body></html>"

    with open(base_path / "index.html", "w") as f:
        f.write(html)

    print("✅ index.html created at /reports/index.html")

if __name__ == "__main__":
    generate_index()
