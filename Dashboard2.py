import streamlit as st
import pandas as pd
import yfinance as yf

st.title("📈 Simple Stock Price App")

tickerSymbol = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, GOOGL)", "AAPL").upper()

start_date = st.date_input("Start Date", pd.to_datetime("2018-05-31"))
end_date = st.date_input("End Date", pd.to_datetime("2020-05-31"))

try:
    tickerdata = yf.Ticker(tickerSymbol)
    tickerDF = tickerdata.history(start=start_date, end=end_date)

    if not tickerDF.empty:
        st.subheader(f"📊 Stock Data for {tickerSymbol}")
        
        st.write("### Closing Price")
        st.line_chart(tickerDF["Close"])

        st.write("### Trading Volume")
        st.line_chart(tickerDF["Volume"])
    else:
        st.warning("⚠️ No data available. Try a different ticker or date range.")
except Exception as e:
    st.error(f"❌ An error occurred: {e}")
