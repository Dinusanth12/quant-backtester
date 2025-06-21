import pandas as pd
from backtester import (
    fetch_data,
    backtest_strategy,
    calculate_metrics,
    plot_with_signals,
    save_trade_log
)

# Import strategies
from strategies.ml_strategy import generate_signals as ml_signals
from strategies.moving_average import generate_signals as sma_signals
from strategies.rsi_strategy import generate_signals as rsi_signals
from strategies.macd_strategy import generate_signals as macd_signals

# --- USER INPUT SECTION ---
tickers_input = input("Enter tickers (comma-separated, e.g., AAPL,MSFT,GOOG): ")
tickers = [t.strip().upper() for t in tickers_input.split(',')]

strategy_choice = input("Choose strategy (SMA, RSI, MACD, ML): ").strip().upper()
start = input("Enter start date (YYYY-MM-DD): ").strip()
end = input("Enter end date (YYYY-MM-DD): ").strip()
# ---------------------------


all_metrics = []

for ticker in tickers:
    print(f"\n📥 Processing {ticker} using {strategy_choice} strategy...")

    # Step 1: Fetch Data
    data = fetch_data(ticker, start, end)

    # Step 2: Apply Selected Strategy
    if strategy_choice == "SMA":
        data = sma_signals(data)
    elif strategy_choice == "RSI":
        data = rsi_signals(data)
    elif strategy_choice == "MACD":
        data = macd_signals(data)
    elif strategy_choice == "ML":
        data = ml_signals(data)
    else:
        raise ValueError("Invalid strategy selected.")


    # Step 3: Backtest
    data, cumulative = backtest_strategy(data)

    # Step 4: Calculate Metrics
    metrics = calculate_metrics(data, cumulative, start, end)
    metrics['Ticker'] = ticker
    all_metrics.append(metrics)

    # Step 5: Save Trade Log + Annotated PnL Chart
    save_trade_log(data, ticker)
    plot_with_signals(data, cumulative, ticker)

# Step 6: Save Combined Metrics Table
df_metrics = pd.DataFrame(all_metrics)
df_metrics.to_csv("results/metrics.csv", index=False)

print("\n✅ All tickers processed! Metrics saved to results/metrics.csv\n")
print(df_metrics)
