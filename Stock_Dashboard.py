import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import timedelta
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Streamlit app header
st.header("Stock Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input("Ticker", value="AAPL")
start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('2023-01-01'))
start_date_adjusted = start_date - timedelta(days=1)

# Fetch stock price data using yfinance
try:
    data = yf.download(ticker, start=start_date_adjusted, end=end_date)
    if data.empty:
        st.error("Invalid ticker or no data available for the given date range.")
    else:
        # Plot stock price data
        fig = px.line(data, x=data.index, y=data['Adj Close'], title=f"{ticker} Stock Price")
        st.plotly_chart(fig)
except Exception as e:
    st.error(f"An error occurred while fetching stock data: {e}")

# Tabs for pricing data, fundamental data, and news
pricing_data, fundamental_data, news = st.tabs(['Pricing Data', 'Fundamental Data', 'Top 10 News'])

# Pricing Data Tab
with pricing_data:
    st.header("Price Movements")
    if not data.empty:
        data2 = data.copy()
        data2["% Change"] = data['Adj Close'] / data["Adj Close"].shift(1) - 1
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return = data2['% Change'].mean() * 252 * 100
        st.write('Annual Return is', annual_return, '%')
        stdev = np.std(data2['% Change']) * np.sqrt(252)
        st.write('Standard Deviation is', stdev * 100, '%')
        st.write('Risk Adjusted Return is', annual_return / (stdev * 100))

# Fundamental Data Tab (Alpha Vantage)
with fundamental_data:
    st.header("Fundamental Data")
    alpha_vantage_key = 'BN3W4QPKLEGHENEE'  # Replace with your Alpha Vantage API key
    fd = FundamentalData(alpha_vantage_key, output_format='pandas')

    try:
        # Fetch Balance Sheet
        st.subheader('Balance Sheet')
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)

        # Fetch Income Statement
        st.subheader('Income Statement')
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)

        # Fetch Cash Flow Statement
        st.subheader('Cash Flow Statement')
        cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cf = cash_flow.T[2:]
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf)
    except Exception as e:
        st.error(f"An error occurred while fetching fundamental data: {e}")

# News Tab
with news:
    st.header(f'News of {ticker}')
    try:
        sn = StockNews(ticker, save_news=False)
        df_news = sn.read_rss()
        for i in range(min(10, len(df_news))):  # Ensure we don't exceed available news
            st.subheader(f'News {i + 1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            title_sentiment = df_news['sentiment_title'][i]
            st.write(f'Title Sentiment: {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment: {news_sentiment}')
    except Exception as e:
        st.error(f"An error occurred while fetching news: {e}")