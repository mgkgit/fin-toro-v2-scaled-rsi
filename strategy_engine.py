# strategy_engine.py
import pandas as pd

def apply_indicators(df, strategy="sma_ema", sma_period=20, ema_period=20, rsi_period=14):
    """
    Apply technical indicators and assign entry/exit signals based on the strategy name.
    Supported: sma_ema, rsi, rsi_sma_combo, bollinger, macd
    """
    df = df.copy()
    df['signal'] = 0  # Reset signals

    # --- Basic Moving Averages ---
    if strategy in ["sma_ema", "rsi_sma_combo"]:
        df['sma'] = df['close'].rolling(window=sma_period).mean()
        df['ema'] = df['close'].ewm(span=ema_period, adjust=False).mean()

    # --- RSI ---
    if strategy in ["rsi", "rsi_sma_combo"]:
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(rsi_period).mean()
        avg_loss = loss.rolling(rsi_period).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))

    # --- Bollinger Bands ---
    if strategy == "bollinger":
        df['ma'] = df['close'].rolling(window=sma_period).mean()
        df['std'] = df['close'].rolling(window=sma_period).std()
        df['upper'] = df['ma'] + 2 * df['std']
        df['lower'] = df['ma'] - 2 * df['std']
        df.loc[df['close'] < df['lower'], 'signal'] = 1  # Buy
        df.loc[df['close'] > df['upper'], 'signal'] = -1  # Sell

    # --- MACD ---
    if strategy == "macd":
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        df.loc[df['macd'] > df['signal_line'], 'signal'] = 1
        df.loc[df['macd'] < df['signal_line'], 'signal'] = -1

    # --- Signal Logic ---
    if strategy == "sma_ema":
        df.loc[df['ema'] > df['sma'], 'signal'] = 1
        df.loc[df['ema'] < df['sma'], 'signal'] = -1

    elif strategy == "rsi":
        df.loc[df['rsi'] < 30, 'signal'] = 1
        df.loc[df['rsi'] > 70, 'signal'] = -1

    elif strategy == "rsi_sma_combo":
        df.loc[(df['rsi'] < 35) & (df['close'] > df['sma']), 'signal'] = 1
        df.loc[(df['rsi'] > 65) & (df['close'] < df['sma']), 'signal'] = -1

    return df.dropna()
