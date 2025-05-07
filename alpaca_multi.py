# alpaca_multi.py
# Author: Monte Krull
# Purpose: Download historical SIP data from Alpaca for multiple tickers
# Requirements: .env, API key, SIP access, installed packages

import os
import argparse
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta
import pandas as pd

# === STEP 1: Load .env API credentials ===
load_dotenv()

def get_config():
    parser = argparse.ArgumentParser(description='Multi-Ticker Alpaca SIP Downloader')
    parser.add_argument('--symbols', type=str, default='AAPL,SPY,TSLA', help='Comma-separated list of tickers')
    parser.add_argument('--timeframe', type=str, default='1Min', help='Timeframe: 1Min, 5Min, etc.')
    parser.add_argument('--days', type=int, default=1, help='Number of past days to fetch')
    args = parser.parse_args()

    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError("❌ Missing API_KEY or SECRET_KEY in .env")

    symbol_list = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    return api_key, secret_key, symbol_list, args.timeframe, args.days

def connect_alpaca(api_key, secret_key):
    base_url = 'https://api.alpaca.markets'
    return REST(api_key, secret_key, base_url=base_url, api_version='v2')

from pandas.tseries.offsets import BDay

def get_historical_data(api, symbol, timeframe, days_back):
        end = datetime.utcnow() - BDay(0)  # or BDay(1) for previous day only
        start = end - BDay(days_back)

        start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f"📡 Fetching {timeframe} bars for {symbol} from {start_str} to {end_str} (SIP)")
        bars = api.get_bars(symbol, timeframe, start=start_str, end=end_str, feed='sip')
        df = bars.df
        if not df.empty:
            df['symbol'] = symbol
        return df

if __name__ == "__main__":
    try:
        api_key, secret_key, symbols, timeframe, days = get_config()
        api = connect_alpaca(api_key, secret_key)

        combined_df = pd.DataFrame()

        for symbol in symbols:
            try:
                df = get_historical_data(api, symbol, timeframe, days)
                if df.empty:
                    print(f"⚠️ No data for {symbol}")
                    continue

                output_file = f"{symbol}_{timeframe}_hist_{days}d.csv"
                df.to_csv(output_file)
                print(f"✅ Saved: {output_file}")
                combined_df = pd.concat([combined_df, df])

            except Exception as symbol_error:
                print(f"❌ Error with {symbol}: {symbol_error}")

        # Optional: Preview combined data
        if not combined_df.empty:
            print("\n📊 Combined preview (first 5 rows across all symbols):")
            print(combined_df.head())
        else:
            print("⚠️ No data fetched for any symbol.")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
