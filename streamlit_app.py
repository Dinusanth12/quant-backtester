import streamlit as st
import pandas as pd
from backtester import (
    fetch_data,
    backtest_strategy,
    calculate_metrics,
    plot_with_signals,
    save_trade_log
)
from strategies.moving_average import generate_signals as sma_signals
from strategies.rsi_strategy import generate_signals as rsi_signals
from strategies.macd_strategy import generate_signals as macd_signals
from strategies.ml_strategy import generate_signals as ml_signals

st.set_page_config(page_title="Quant Backtester", layout="wide")
st.title("📈 Quant Backtester")
st.markdown("Run backtests on real financial data using technical or ML strategies.")

# 📦 Cache data to avoid repeated downloads
@st.cache_data(show_spinner=False)
def cached_fetch_data(ticker, start, end):
    return fetch_data(ticker, start, end)

# 🔧 User Input
tickers = st.text_input("Enter tickers (comma-separated)", "AAPL,MSFT,GOOG")
start = st.date_input("Start Date", pd.to_datetime("2018-01-01"))
end = st.date_input("End Date", pd.to_datetime("2024-12-31"))
strategy_choice = st.selectbox("Select Strategy", ["SMA", "RSI", "MACD", "ML"])

# ▶️ Run button
if st.button("Run Backtest"):
    ticker_list = [t.strip().upper() for t in tickers.split(',')]
    all_metrics = []
    progress = st.progress(0)
    progress_step = 1 / len(ticker_list)

    with st.spinner("Running backtests..."):
        for i, ticker in enumerate(ticker_list):
            st.markdown(f"### 🔄 Processing `{ticker}` with `{strategy_choice}` strategy")

            try:
                # ⬇ Fetch and generate signals
                data = cached_fetch_data(ticker, str(start), str(end))

                if strategy_choice == "SMA":
                    data = sma_signals(data)
                elif strategy_choice == "RSI":
                    data = rsi_signals(data)
                elif strategy_choice == "MACD":
                    data = macd_signals(data)
                elif strategy_choice == "ML":
                    data = ml_signals(data)

                # 📈 Backtest + Metrics
                data, cumulative = backtest_strategy(data)
                metrics = calculate_metrics(data, cumulative, start, end)
                metrics['Ticker'] = ticker
                all_metrics.append(metrics)

                # 💾 Save outputs
                plot_with_signals(data, cumulative, ticker)
                save_trade_log(data, ticker)

                # 📊 Display Tabs
                with st.expander(f"📊 View {ticker} Results"):
                    tab1, tab2, tab3 = st.tabs(["📈 Chart", "📋 Metrics", "📄 Trade Log"])
                    tab1.image(f"results/{ticker}_pnl_signals.png", use_container_width=True)
                    tab2.dataframe(pd.DataFrame([metrics]))
                    tab3.dataframe(pd.read_csv(f"results/{ticker}_trade_log.csv"))

            except Exception as e:
                st.error(f"❌ Error processing {ticker}: {e}")

            progress.progress(min((i + 1) * progress_step, 1.0))

    # 📥 Final Metrics Export
    if all_metrics:
        df_metrics = pd.DataFrame(all_metrics)
        st.success("✅ Backtest complete for all tickers!")
        st.download_button("📥 Download Full Metrics CSV", df_metrics.to_csv(index=False), "metrics.csv", "text/csv")
