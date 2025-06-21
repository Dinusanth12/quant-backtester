import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for image saving
import matplotlib.pyplot as plt
import os


def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, auto_adjust=False)
    expected_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    available_cols = [col for col in expected_cols if col in data.columns]
    data = data[available_cols]
    data.dropna(inplace=True)
    return data

def backtest_strategy(data):
    data['Returns'] = data['Close'].pct_change()
    data['Strategy'] = data['Signal'].shift(1) * data['Returns']
    data.dropna(inplace=True)
    cumulative = (1 + data[['Returns', 'Strategy']]).cumprod()
    return data, cumulative

def calculate_metrics(data, cumulative, start_date, end_date):
    total_return = cumulative['Strategy'].iloc[-1] - 1
    sharpe = np.sqrt(252) * data['Strategy'].mean() / data['Strategy'].std()
    drawdown = (data['Strategy'].cumsum().cummax() - data['Strategy'].cumsum()).max()
    volatility = np.std(data['Strategy']) * np.sqrt(252)

    days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
    cagr = (cumulative['Strategy'].iloc[-1]) ** (365.0 / days) - 1
    calmar = cagr / drawdown if drawdown != 0 else np.nan

    # Trade stats
    trades = data[data['Signal'].diff() != 0]
    trade_count = len(trades)
    trade_returns = trades['Strategy']
    wins = trade_returns[trade_returns > 0]
    win_rate = len(wins) / trade_count if trade_count > 0 else 0

    # Consecutive losses
    loss_streak = 0
    max_loss_streak = 0
    for r in trade_returns:
        if r < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        else:
            loss_streak = 0

    return {
        'Total Return (%)': round(total_return * 100, 2),
        'CAGR (%)': round(cagr * 100, 2),
        'Sharpe Ratio': round(sharpe, 2),
        'Calmar Ratio': round(calmar, 2),
        'Volatility (%)': round(volatility * 100, 2),
        'Max Drawdown (%)': round(drawdown * 100, 2),
        'Trade Count': trade_count,
        'Win Rate (%)': round(win_rate * 100, 2),
        'Max Consecutive Losses': max_loss_streak
    }

def plot_with_signals(data, cumulative, ticker):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(cumulative.index, cumulative['Strategy'], label='Strategy', color='blue')
    ax.plot(cumulative.index, cumulative['Returns'], label='Market', linestyle='--', color='grey')

    buys = data[data['Signal'] == 1]
    sells = data[data['Signal'] == -1]

    ax.plot(buys.index, cumulative.loc[buys.index, 'Strategy'], '^', markersize=10, color='green', label='Buy')
    ax.plot(sells.index, cumulative.loc[sells.index, 'Strategy'], 'v', markersize=10, color='red', label='Sell')

    ax.set_title(f'{ticker} Strategy with Buy/Sell Signals')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cumulative Returns')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    os.makedirs("results", exist_ok=True)
    plt.savefig(f"results/{ticker}_pnl_signals.png")
    plt.close()

def save_trade_log(data, ticker):
    trades = data[data['Signal'].diff() != 0].copy()
    trades['Trade Type'] = trades['Signal'].apply(lambda x: 'Buy' if x == 1 else 'Sell')
    trades['Date'] = trades.index
    trades['Return'] = trades['Strategy']
    trades = trades[['Date', 'Close', 'Trade Type', 'Return']]
    trades.to_csv(f"results/{ticker}_trade_log.csv", index=False)
