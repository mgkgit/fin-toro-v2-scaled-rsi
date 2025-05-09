# strategy_engine.py

import pandas as pd


def apply_indicators(df, strategy="sma_ema", **kwargs):
    df = df.copy()
    df['signal'] = 0

    if strategy == "sma_ema":
        sma = kwargs.get("sma", 20)
        ema = kwargs.get("ema", 20)
        df['sma'] = df['close'].rolling(window=sma).mean()
        df['ema'] = df['close'].ewm(span=ema, adjust=False).mean()
        df.loc[df['ema'] > df['sma'], 'signal'] = 1
        df.loc[df['ema'] < df['sma'], 'signal'] = -1

    elif strategy == "macd":
        fast = kwargs.get("fast", 12)
        slow = kwargs.get("slow", 26)
        signal = kwargs.get("signal", 9)
        df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df.loc[df['macd'] > df['macd_signal'], 'signal'] = 1
        df.loc[df['macd'] < df['macd_signal'], 'signal'] = -1

    elif strategy == "bollinger":
        period = kwargs.get("sma", 20)
        stddev = kwargs.get("stddev", 2)
        df['sma'] = df['close'].rolling(window=period).mean()
        df['std'] = df['close'].rolling(window=period).std()
        df['upper'] = df['sma'] + stddev * df['std']
        df['lower'] = df['sma'] - stddev * df['std']
        df.loc[df['close'] < df['lower'], 'signal'] = 1
        df.loc[df['close'] > df['upper'], 'signal'] = -1

    else:
        raise ValueError(f"Strategy '{strategy}' not recognized.")

    return df.dropna()
