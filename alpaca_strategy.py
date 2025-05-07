# alpaca_strategy.py
# Author: Monte Krull
# Adds SMA/EMA crossover strategy to historical SIP data from Alpaca

import os
import argparse
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta
import pandas as pd
from pandas.tseries.offsets import BDay

# === STEP 1: Load .env Credentials ===
load_dotenv()

def get_config():
    parser = argparse.ArgumentParser(description='Alpaca SIP Strategy Downloader')
    parser.add_argument('--symbols', type=str, default='AAPL,SPY', help='Comma-separated list of tickers')
    parser.add_argument('--timeframe', type=str, default='5Min', help='Timeframe: 1Min, 5Min, 15Min, etc.')
    parser.add_argument('--days', type=int, default=2, help='How many past business days to fetch')
    args = parser.parse_args()

    api_key = os.getenv('API_KEY')
    secret_key = os.getenv('SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError("❌ Missing API credentials in .env")

    symbol_list = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    return api_key, secret_key, symbol_list, args.timeframe, args.days

def connect_alpaca(api_key, secret_key):
    return REST(api_key, secret_key, base_url='https://api.alpaca.markets', api_version='v2')

def get_historical_data(api, symbol, timeframe, days_back):
    end = datetime.utcnow() - BDay(0)
    start = end - BDay(days_back)

    start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"📡 Fetching {timeframe} bars for {symbol} from {start_str} to {end_str} (SIP)")
    bars = api.get_bars(symbol, timeframe, start=start_str, end=end_str, feed='sip')
    df = bars.df

    if not df.empty:
        df['symbol'] = symbol
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()

        # Generate signal: Buy when EMA crosses above SMA
        df['signal'] = 0
        df.loc[df['ema_20'] > df['sma_20'], 'signal'] = 1  # Buy
        df.loc[df['ema_20'] < df['sma_20'], 'signal'] = -1  # Sell

    return df

if __name__ == "__main__":
    try:
        api_key, secret_key, symbols, timeframe, days = get_config()
        api = connect_alpaca(api_key, secret_key)

        all_data = []

        for symbol in symbols:
            try:
                df = get_historical_data(api, symbol, timeframe, days)
                if df.empty:
                    print(f"⚠️ No data for {symbol}")
                    continue

                output_file = f"{symbol}_{timeframe}_strategy_{days}d.csv"
                df.to_csv(output_file)
                print(f"✅ Strategy file saved: {output_file}")
                all_data.append(df)

            except Exception as e:
                print(f"❌ Error for {symbol}: {e}")

        if all_data:
            combined = pd.concat(all_data)
            print("\n📊 Strategy preview (first 5 rows):")
            print(combined[['close', 'sma_20', 'ema_20', 'signal']].head())
        else:
            print("⚠️ No strategy data available.")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
