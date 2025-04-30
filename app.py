import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime as dt, timedelta as td

st.set_page_config(layout="wide")

@st.cache_data
def load_main_tickers():
    return {
        'PETR4.SA': 'Petrobras',
        'VALE3.SA': 'Vale',
        'ITUB4.SA': 'Itaú',
        'B3SA3.SA': 'B3',
        'ABEV3.SA': 'Ambev',
        'WEGE3.SA': 'Weg',
        'BBAS3.SA': 'Banco do Brasil',
        'RENT3.SA': 'Localiza',
        'LREN3.SA': 'Lojas Renner',
    }

@st.cache_data
def load_data(tickers_dict):
    tickers = list(tickers_dict.keys())
    names = list(tickers_dict.values())
    start_date = '2010-01-01'
    end_date = dt.today().strftime('%Y-%m-%d')

    stock_data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')

    close_prices = pd.DataFrame()

    for ticker, name in tickers_dict.items():
        try:
            close_prices[name] = stock_data[ticker]['Close']
        except KeyError:
            st.warning(f"⚠️ No data found for ticker: {ticker}")
    
    return close_prices

main_tickers = load_main_tickers()
data = load_data(main_tickers)

st.title("📈 Brazilian Stock Dashboard")
st.markdown("Visualize the historical performance of major Brazilian stocks.")

st.sidebar.header('Filters')
selected_stocks = st.sidebar.multiselect(
    'Select assets to view',
    options=data.columns.tolist(),
    default=['Lojas Renner']
)

if selected_stocks:
    data = data[selected_stocks]

if not data.empty:
    data.index = pd.to_datetime(data.index)
    initial_date = data.index.min().to_pydatetime()
    final_date = data.index.max().to_pydatetime()
else:
    st.error("Error: No data loaded. Check tickers or internet connection.")
    st.stop()

slider = st.sidebar.slider(
    'Select time range',
    min_value=initial_date, 
    max_value=final_date, 
    value=(initial_date, final_date),
    step=td(days=1)
)

data = data.loc[slider[0]:slider[1]]

st.line_chart(data)

summary = ""
portfolio = [1000 for _ in selected_stocks]
initial_total = sum(portfolio)

for i, stock in enumerate(selected_stocks):
    perf = data[stock].iloc[-1] / data[stock].iloc[0] - 1
    portfolio[i] = portfolio[i] * (1 + perf)

    if perf > 0:
        summary += f"  \n{stock}: :green[{perf:.1%}]"
    elif perf < 0:
        summary += f"  \n{stock}: :red[{perf:.1%}]"
    else:
        summary += f"  \n{stock}: {perf:.1%}"

final_total = sum(portfolio)
total_perf = final_total / initial_total - 1

if total_perf > 0:
    summary += f"\n\nTotal portfolio performance: :green[{total_perf:.1%}]"
elif total_perf < 0:
    summary += f"\n\nTotal portfolio performance: :red[{total_perf:.1%}]"
else:
    summary += f"\n\nTotal portfolio performance: {total_perf:.1%}"

st.markdown("### 📊 Asset Performance Summary")
st.markdown(summary)

st.sidebar.markdown("Developed by [André](https://github.com/nine913)")
