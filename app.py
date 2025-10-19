import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import base64
import yfinance as yf
import time
from functools import wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Import curl_cffi for bypassing Yahoo Finance TLS fingerprinting
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    st.warning("⚠️ curl_cffi not installed. Install it with: pip install curl-cffi")

st.set_page_config(layout="wide", page_title="Crypto & Stock Dashboard")
st.title("📊 Crypto & Stock Dashboard")

st.sidebar.header("Navigation")
app_mode = st.sidebar.selectbox("Choose App Mode", ["Crypto Prices", "Stock Prices"])


def rate_limited(max_per_minute):
    """Rate limiting decorator to control API request frequency"""
    min_interval = 60.0 / max_per_minute
    
    def decorator(func):
        last_call = {'time': 0.0}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call['time']
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_call['time'] = time.time()
            return result
        
        return wrapper
    return decorator

def download_link(df, filename="data.csv"):
    """Generate download link for DataFrame"""
    csv = df.to_csv(index=False).encode()
    b64 = base64.b64encode(csv).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'

# Crypto Functions

load_dotenv()
API_KEY = os.getenv("api_key")
CMC_URL = os.getenv("cmc_url")

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

@st.cache_data(ttl=300, show_spinner="Fetching crypto data...")
@rate_limited(20)
def fetch_crypto_data(currency="USD"):
    """Fetch cryptocurrency data from CoinMarketCap API"""
    params = {"start": "1", "limit": "100", "convert": currency}
    
    try:
        response = requests.get(CMC_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            coins = data['data']
            
            df = pd.DataFrame(coins)
            df = df[['name', 'symbol', 'quote']]
            
            # Extract price and change data
            df['price'] = df['quote'].apply(lambda x: x.get(currency, {}).get('price'))
            df['percent_change_1h'] = df['quote'].apply(lambda x: x.get(currency, {}).get('percent_change_1h'))
            df['percent_change_24h'] = df['quote'].apply(lambda x: x.get(currency, {}).get('percent_change_24h'))
            df['percent_change_7d'] = df['quote'].apply(lambda x: x.get(currency, {}).get('percent_change_7d'))
            
            df = df[['name', 'symbol', 'price', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']]
            df = df.dropna()
            return df
        else:
            data = response.json()
            error_msg = data.get('status', {}).get('error_message', 'Unknown error')
            st.error(f"Failed to fetch data: {response.status_code} - {error_msg}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Stock Functions with TLS Fingerprinting Bypass

@st.cache_data(ttl=300, show_spinner="Fetching stock data...")
@rate_limited(30)
def fetch_stock_data(ticker_symbol, start_date, end_date):
    """Fetch stock data from Yahoo Finance with TLS fingerprinting bypass"""
    try:
        # Create session with Chrome impersonation to bypass Yahoo's TLS fingerprinting
        if CURL_CFFI_AVAILABLE:
            session = curl_requests.Session(impersonate="chrome")
            ticker = yf.Ticker(ticker_symbol, session=session)
        else:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            })
            ticker = yf.Ticker(ticker_symbol, session=session)
        
        # Fetch historical data
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        return df
        
    except Exception as e:
        error_str = str(e).lower()
        if "too many requests" in error_str or "rate limit" in error_str or "429" in error_str:
            if not CURL_CFFI_AVAILABLE:
                st.error("⚠️ Yahoo Finance rate limit detected. Please install curl-cffi:")
                st.code("pip install curl-cffi", language="bash")
            else:
                st.warning("⚠️ Rate limit still encountered. Waiting 60 seconds before retry...")
                time.sleep(60)
        else:
            st.error(f"Error fetching stock data: {e}")
        return None

# Crypto App Mode

if app_mode == "Crypto Prices":
    st.sidebar.header("Crypto Settings")
    currency_unit = st.sidebar.selectbox("Select Currency", ["USD", "BTC", "ETH"])
    
    with st.spinner("Loading cryptocurrency data..."):
        df_crypto = fetch_crypto_data(currency_unit)
    
    if df_crypto is not None and not df_crypto.empty:
        coins = sorted(df_crypto['symbol'].unique())
        default_selection = coins[:10] if len(coins) >= 10 else coins
        
        selected_coins = st.sidebar.multiselect(
            "Select Cryptocurrencies", 
            coins, 
            default=default_selection
        )
        
        if selected_coins:
            df_selected = df_crypto[df_crypto['symbol'].isin(selected_coins)].copy()
            
           
            st.subheader(f"💰 Crypto Prices ({currency_unit})")
            
           
            df_display = df_selected.copy()
            df_display['price'] = df_selected['price'].apply(
                lambda x: f"${x:,.2f}" if currency_unit == "USD" else f"{x:.8f}"
            )
            
            st.dataframe(df_display, use_container_width=True)
            st.markdown(download_link(df_selected, "crypto_data.csv"), unsafe_allow_html=True)
            
           
            st.subheader("📈 Price Change Analysis")
            
            timeframe = st.sidebar.selectbox("Select Timeframe", ["1h", "24h", "7d"])
            col_map = {
                "1h": "percent_change_1h", 
                "24h": "percent_change_24h", 
                "7d": "percent_change_7d"
            }
            
            
            df_viz = df_crypto[df_crypto['symbol'].isin(selected_coins)].copy()
            df_viz[col_map[timeframe]] = pd.to_numeric(df_viz[col_map[timeframe]], errors="coerce")
            df_viz = df_viz.dropna(subset=[col_map[timeframe]])
            
            if not df_viz.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                
               
                colors = ['green' if x > 0 else 'red' for x in df_viz[col_map[timeframe]]]
                
                ax.bar(df_viz['symbol'], df_viz[col_map[timeframe]], color=colors, alpha=0.7)
                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
                ax.set_xlabel("Cryptocurrency Symbol", fontsize=12)
                ax.set_ylabel(f"Percentage Change ({timeframe})", fontsize=12)
                ax.set_title(f"Crypto Price Change Over {timeframe}", fontsize=14, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                st.pyplot(fig)
                plt.close()
            else:
                st.warning("No valid data available for the selected timeframe.")
        else:
            st.info("👆 Please select at least one cryptocurrency from the sidebar.")
    else:
        st.warning("⚠️ Unable to fetch cryptocurrency data. Please check your API key or internet connection.")

# Stock App Mode

elif app_mode == "Stock Prices":
    st.sidebar.header("Stock Settings")
    
    # Show curl_cffi status
    if CURL_CFFI_AVAILABLE:
        st.sidebar.success("✅ curl_cffi enabled (bypasses rate limits)")
    else:
        st.sidebar.error("❌ curl_cffi not installed")
        st.sidebar.info("Install with: pip install curl-cffi")
    
    ticker_symbol = st.sidebar.text_input(
        "Enter Stock Ticker", 
        value="AAPL",
        help="Enter stock symbol (e.g., AAPL, TSLA, GOOGL)"
    ).upper()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=datetime.now() - timedelta(days=365)
        )
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=datetime.now()
        )
    
    if start_date >= end_date:
        st.error("❌ Start date must be before end date.")
    elif ticker_symbol:
        df_stock = fetch_stock_data(ticker_symbol, start_date, end_date)
        
        if df_stock is not None and not df_stock.empty:
            st.subheader(f"📊 Stock Data for {ticker_symbol}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"${df_stock['Close'].iloc[-1]:.2f}")
            with col2:
                price_change = df_stock['Close'].iloc[-1] - df_stock['Close'].iloc[0]
                st.metric("Change", f"${price_change:.2f}", 
                         delta=f"{(price_change/df_stock['Close'].iloc[0]*100):.2f}%")
            with col3:
                st.metric("Highest", f"${df_stock['High'].max():.2f}")
            with col4:
                st.metric("Lowest", f"${df_stock['Low'].min():.2f}")
            
            st.write("### 📈 Closing Price")
            st.line_chart(df_stock["Close"], use_container_width=True)
            
            st.write("### 📊 Trading Volume")
            st.bar_chart(df_stock["Volume"], use_container_width=True)
            
            st.markdown(download_link(df_stock.reset_index(), f"{ticker_symbol}_stock_data.csv"), 
                       unsafe_allow_html=True)
            
            with st.expander("View Raw Data"):
                st.dataframe(df_stock, use_container_width=True)
        else:
            st.warning(f"⚠️ No data available for ticker '{ticker_symbol}'. Please check the symbol or try a different date range.")
    else:
        st.info("👆 Please enter a stock ticker symbol in the sidebar.")
