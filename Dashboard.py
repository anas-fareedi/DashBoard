# Crypto Price App using CoinMarketCap API
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import base64

# Set Streamlit page layout
st.set_page_config(layout="wide")
st.title('Crypto Price App')

# Sidebar
st.sidebar.header('Input Options')
currency_price_unit = st.sidebar.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))
 
API_KEY = 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c'  # Replace with your API key
URL = "https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}
def fetch_crypto_data():
    parameters = {
        'start':'1',
        'limit':'5000', #Increased limit to get more coins
        'convert':currency_price_unit
    }
    try:
        session = requests.Session()
        response = session.get(URL, params=parameters, headers=headers)
        data = response.json()
        if response.status_code == 200:
            coins = data['data']
            df = pd.DataFrame(coins)
            df = df[['name', 'symbol', 'quote']]

            #Extract prices and percentage changes. More robust handling of missing data.
            df['price'] = df['quote'].apply(lambda x: x.get(currency_price_unit, {}).get('price'))
            df['percent_change_1h'] = df['quote'].apply(lambda x: x.get(currency_price_unit, {}).get('percent_change_1h'))
            df['percent_change_24h'] = df['quote'].apply(lambda x: x.get(currency_price_unit, {}).get('percent_change_24h'))
            df['percent_change_7d'] = df['quote'].apply(lambda x: x.get(currency_price_unit, {}).get('percent_change_7d'))

            df = df[['name', 'symbol', 'price', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']]
            return df
        else:
            st.error(f"Failed to fetch data. Status Code: {response.status_code}")
            st.error(data.get('status', {}).get('error_message')) #Display error message from CMC API
            return None

    except requests.exceptions.ConnectionError as e:
        st.error(f"Connection error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None
# Load Data
df = fetch_crypto_data()

if df is not None:
    # Cryptocurrency selection
    sorted_coin = sorted(df['symbol'].unique()) #Use .unique() to avoid duplicates in sorted list
    selected_coin = st.sidebar.multiselect('Cryptocurrency', sorted_coin, sorted_coin[:10]) #Default selection of first 10

    if selected_coin: #Check if any coins are selected
        df_selected = df[df['symbol'].isin(selected_coin)]

        # Display Data
        st.subheader('Price Data of Selected Cryptocurrency')
        st.dataframe(df_selected)

        def file_download(df):
            csv = df.to_csv(index=False).encode()  # Encode to bytes
            b64 = base64.b64encode(csv).decode()  # Decode to string
            return f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'

        st.markdown(file_download(df_selected), unsafe_allow_html=True)

        # Select timeframe for price change
        st.subheader('Price Change Over Time')
        percent_timeframe = st.sidebar.selectbox('Select Timeframe', ['1h', '24h', '7d'])
        percent_map = {"1h": 'percent_change_1h', "24h": 'percent_change_24h', "7d": 'percent_change_7d'}

        # Convert to numeric and handle errors
        df_selected[percent_map[percent_timeframe]] = pd.to_numeric(df_selected[percent_map[percent_timeframe]], errors='coerce')
        df_selected = df_selected.dropna(subset=[percent_map[percent_timeframe]])

        if not df_selected.empty:
            plt.figure(figsize=(10, 5)) #Create the figure before plotting
            plt.bar(df_selected['symbol'], df_selected[percent_map[percent_timeframe]], color="skyblue") #Use plt.bar directly
            plt.xlabel("Cryptocurrency Symbol")
            plt.ylabel(f"Percentage Change ({percent_timeframe})")
            plt.title(f"Price Change Over {percent_timeframe}")
            st.pyplot(plt) #Use st.pyplot after creating the plot
        else:
            st.warning(f"No valid data available for {percent_timeframe} for the selected cryptocurrencies.")
    else:
        st.warning("Please select at least one cryptocurrency.")
else:
    st.warning("No data available. Check your API key, internet connection, or ensure you are using the correct CoinMarketCap Pro API.")