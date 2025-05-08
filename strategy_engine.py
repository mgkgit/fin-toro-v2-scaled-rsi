import pandas as pd

def apply_indicators(df, strategy="sma_ema", sma_period=20, ema_period=20, rsi_period=14):
    df = df.copy()

    df['sma'] = df['close'].rolling(window=sma_period).mean()
    df['ema'] = df['close'].ewm(span=ema_period, adjust=False).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['signal'] = 0

    if strategy == "sma_ema":
        df.loc[df['ema'] > df['sma'], 'signal'] = 1
        df.loc[df['ema'] < df['sma'], 'signal'] = -1
    elif strategy == "rsi":
        df.loc[df['rsi'] < 30, 'signal'] = 1
        df.loc[df['rsi'] > 70, 'signal'] = -1
    elif strategy == "rsi_sma_combo":
        df.loc[(df['rsi'] < 35) & (df['close'] > df['sma']), 'signal'] = 1
        df.loc[(df['rsi'] > 65) & (df['close'] < df['sma']), 'signal'] = -1
    else:
        raise ValueError(f"Unsupported strategy: {strategy}")

    return df.dropna()
