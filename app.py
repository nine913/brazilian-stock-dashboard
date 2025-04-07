import streamlit as st
import yfinance as yf
from datetime import datetime as dt, timedelta as td

st.set_page_config(layout="wide")

@st.cache_data
def load_data(tickers):
    end = dt.today().strftime('%Y-%m-%d')
    start = '2010-01-01'
    data = yf.download(tickers, start=start, end=end)['Close']
    return data

main_tickers = {
    'PETR4.SA': 'Petrobras',
    'VALE3.SA': 'Vale',
    'ITUB4.SA': 'Itaú Unibanco',
    'B3SA3.SA': 'B3',
    'ABEV3.SA': 'Ambev',
    'BBAS3.SA': 'Banco do Brasil'
}

tickers = list(main_tickers.keys())
data = load_data(tickers)
data = data.rename(columns=main_tickers)

st.title("📈 Brazilian Stock Dashboard")
st.write("The graph below shows the historical closing prices of selected major Brazilian stocks.")

st.sidebar.header("Filters")
stock_list = st.sidebar.multiselect("Select stocks", data.columns.tolist(), default=data.columns.tolist())

initial_date = data.index.min().to_pydatetime()
final_date = data.index.max().to_pydatetime()

date_range = st.sidebar.slider("Select date range",
                               min_value=initial_date,
                               max_value=final_date,
                               value=(initial_date, final_date),
                               step=td(days=1))

filtered_data = data[stock_list].loc[date_range[0]:date_range[1]]

st.line_chart(filtered_data)

initial_investment = 1000
portfolio = [initial_investment] * len(stock_list)
text_stock = ""

for i, stock in enumerate(stock_list):
    perf = filtered_data[stock].iloc[-1] / filtered_data[stock].iloc[0] - 1
    portfolio[i] *= (1 + perf)
    if perf > 0:
        text_stock += f"  \n{stock}: :green[{perf:.1%}]"
    elif perf < 0:
        text_stock += f"  \n{stock}: :red[{perf:.1%}]"
    else:
        text_stock += f"  \n{stock}: {perf:.1%}"

total_initial = initial_investment * len(stock_list)
total_final = sum(portfolio)
overall_perf = total_final / total_initial - 1

if overall_perf > 0:
    text_portfolio = f"Portfolio performance: :green[{overall_perf:.1%}]"
elif overall_perf < 0:
    text_portfolio = f"Portfolio performance: :red[{overall_perf:.1%}]"
else:
    text_portfolio = f"Portfolio performance: {overall_perf:.1%}"

st.markdown(f"""
### 📊 Performance Summary

{text_stock}

{text_portfolio}
""")

st.sidebar.markdown("Developed by [André](https://github.com/nine913)")
