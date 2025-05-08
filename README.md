# 📊 Fin-Toro V2 – Scaled Strategy Engine

A modular, backtest-driven trading framework supporting:
- 📈 SMA/EMA, RSI, and combo logic
- 🔁 Dynamic leverage and bet sizing
- ✅ Scaling entries/exits
- 📄 Auto-generated strategy reports (HTML + PDF)

### 🧪 Features

- Supports multi-symbol strategy testing
- Batch equity curve, PnL, and drawdown charting
- Clean folder structure for trade logs and results
- JSON-based config input for each symbol
- GitHub Pages–ready reporting dashboard

### 🚀 Quick Start

```bash
# Activate environment
source .venv/bin/activate

# Run strategy & reporting for all symbols
python batch_generate_reports.py

# Open generated summary
open index.html
