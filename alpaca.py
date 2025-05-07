# alpaca.py
# Author: Monte Krull
# Purpose: Pull historical SIP data from Alpaca for backtesting.
# Requirements:
# - Alpaca LIVE account with SIP market data access
# - .env file in project root with API_KEY and SECRET_KEY
# - python-dotenv, alpaca-trade-api, pandas installed

import os
import argparse
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta
import pandas as pd

# === STEP 1: Load credentials from .env file ===
# The .env file must contain API_KEY and SECRET_KEY
load_dotenv()

# === STEP 2: Parse CLI arguments for symbol, timeframe, days ===
def get_config():
    parser = argparse.ArgumentParser(description='Alpaca Historical SIP Data Downloader')
    parser.add_argument('--symbol', type=str, default='SPY', help='Ticker symbol, e.g. AAPL, TSLA')
    parser.add_argument('--timeframe', type=str, default='1Min', help='Timeframe: 1Min, 5Min, 15Min, etc.')
    parser.add_argument('--days', type=int, default=1, help='Number of past days to retrieve')
    args = parser.parse_args()

    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError("❌ Missing API credentials. Please set API_KEY and SECRET_KEY in a .env file.")

    return api_key, secret_key, args.symbol.upper(), args.timeframe, args.days

# === STEP 3: Connect to Alpaca LIVE endpoint ===
def connect_alpaca(api_key, secret_key):
    base_url = 'https://api.alpaca.markets'
    return REST(api_key, secret_key, base_url=base_url, api_version='v2')

# === STEP 4: Pull historical SIP data with valid RFC 3339 formatting ===
def get_historical_data(api, symbol, timeframe, days_back):
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)

    # Format timestamps without microseconds (required by Alpaca API)
    start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"📡 Fetching {timeframe} bars for {symbol} from {start_str} to {end_str} (SIP feed)")
    bars = api.get_bars(
        symbol,
        timeframe,
        start=start_str,
        end=end_str,
        feed='sip'
    )
    df = bars.df
    return df

# === STEP 5: Main execution ===
if __name__ == "__main__":
    try:
        api_key, secret_key, symbol, timeframe, days = get_config()
        api = connect_alpaca(api_key, secret_key)
        df = get_historical_data(api, symbol, timeframe, days)

        if df.empty:
            print(f"⚠️ No data returned for {symbol}. Try a different timeframe or verify market access.")
        else:
            print(f"✅ Retrieved {len(df)} bars for {symbol}")
            output_file = f"{symbol}_{timeframe}_hist_{days}d.csv"
            df.to_csv(output_file)
            print(f"💾 Data saved to {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
