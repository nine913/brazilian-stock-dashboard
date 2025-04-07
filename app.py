import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta as td

st.set_page_config(layout="wide")

@st.cache_data
def load_data(businesses):
    text_ticker = " ".join(businesses)
    stock_data = yf.Tickers(businesses)
    quotes = stock_data.history(period='1d', start='2010-01-01', end='2024-07-01')
    quotes = quotes['Close']
    return quotes

@st.cache_data
def load_data2():
    base = pd.read_csv(r'IBOV.csv', sep=';')
    tickers = list(base['Código'])
    tickers = [ticker + '.SA' for ticker in tickers]
    return tickers

stocks = load_data2()
data = load_data(stocks)

st.write("""
# Stock Prices App
The graph below represents the evolution of the share price over the years
""")

st.sidebar.header('Filters')


stock_list = st.sidebar.multiselect('Select options to view', data.columns)
if stock_list:
    data = data[stock_list]
    if len(stock_list) == 1:
        single_stock = stock_list[0]
        data = data.rename(columns={single_stock: 'Close'})


initial_date = data.index.min().to_pydatetime()
final_date = data.index.max().to_pydatetime()

slider = st.sidebar.slider('Select period',
                   min_value=initial_date, 
                   max_value=final_date, 
                   value=(initial_date, final_date),
                   step=td(days=1))
        
data = data.loc[slider[0]:slider[1]]


st.line_chart(data)

text_stock = ''

if len(stock_list) == 0:
    stock_list = list(data.columns)
elif len(stock_list) == 1:
    data = data.rename(columns={'Close': single_stock})

portfolio = [1000 for stock in stock_list]
initial_portfolio_total = sum(portfolio)

for i, stock in enumerate(stock_list):
    performance = data[stock].iloc[-1] / data[stock].iloc[0] - 1 
    performance = float(performance)

    portfolio[i] = portfolio[i] * (1 + performance)

    if performance > 0:
        text_stock = text_stock + f'  \n{stock}: :green[{performance:.1%}]'
    elif performance < 0:
        text_stock = text_stock + f'  \n{stock}: :red[{performance:.1%}]'
    else:
        text_stock = text_stock + f'  \n{stock}: {performance:.1%}'

final_portfolio_total = sum(portfolio)
portfolio_performance = final_portfolio_total / initial_portfolio_total - 1 


if portfolio_performance > 0:
    text_portfolio = f'Portfolio performance with all assets: :green[{portfolio_performance:.1%}]'
elif portfolio_performance < 0:
    text_portfolio = f'Portfolio performance with all assets: :red[{portfolio_performance:.1%}]'
else:
    text_portfolio = f'Portfolio performance with all assets: {portfolio_performance:.1%}'

st.write(f"""
### Asset performance
This is the performance of the selected assets over time:

{text_stock}

{text_portfolio}
""")

st.sidebar.markdown('Developed by [André](https://github.com/nine913)')