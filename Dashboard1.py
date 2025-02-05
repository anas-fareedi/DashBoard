import streamlit as st
import pandas as pd
import yfinance as yf

st.write("""
         # Simple Stock Price App
         
         Shown below are the stock price and volume of Google.
         """)

tickerSymbol = "AAPL"
tickerdata = yf.Ticker(tickerSymbol)

tickerDF = tickerdata.history(start="2018-05-31", end="2020-05-31")

# if data is not empty

if not tickerDF.empty:
    st.write("### Closing Price")
    st.line_chart(tickerDF["Close"])

    st.write("### Trading Volume")
    st.line_chart(tickerDF["Volume"])
else:
    st.error("No data available. Try a different date range or check internet connection.")
