# batch_run.py

import json
import subprocess

symbols = ["SPY", "SSO", "UPRO"]  # Add more as needed

for symbol in symbols:
    print(f"\n🚀 Running pipeline for: {symbol}")

    # Update config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    config["symbol"] = symbol
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Run the full pipeline
    subprocess.run(["python", "run_advanced_backtest.py"])
    subprocess.run(["python", "plot_advanced_results.py"])
    subprocess.run(["python", "generate_advanced_report.py"])
