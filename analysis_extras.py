def calculate_sharpe_ratio(equity_df, risk_free_rate=0.0):
    equity_df = equity_df.copy()
    equity_df['returns'] = equity_df['equity'].pct_change()
    excess_returns = equity_df['returns'] - risk_free_rate
    sharpe = excess_returns.mean() / excess_returns.std()
    return sharpe * (252 * 78)**0.5 if sharpe and sharpe != float('inf') else 0

def calculate_volatility(equity_df):
    returns = equity_df['equity'].pct_change().dropna()
    return returns.std() * (252 * 78)**0.5  # Annualized intraday volatility
