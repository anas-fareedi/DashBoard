# 📊 Crypto & Stock Dashboard

A comprehensive Streamlit web application for tracking cryptocurrency prices and stock market data in real-time.

### ✨ Features

Monitor top 100 cryptocurrencies with live prices

View crypto prices in USD, BTC, or ETH

Visualize percentage changes over 1h, 24h, 7d

Track historical stock prices from Yahoo Finance

Interactive charts with color-coded price changes

Download data as CSV

Built-in rate limiting to avoid API throttling

## 🚀 Installation

### Prerequisites

```
Python 3.8 or higher

pip package manager
```

## Setup

### Clone the repository
```
git clone https://github.com/yourusername/crypto-stock-dashboard.git
cd crypto-stock-dashboard
```

### Create a virtual environment (recommended)
```
python -m venv venv
# On Linux/Mac
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### 🔑 API Keys

CoinMarketCap API (Required for Crypto)

Sign up at CoinMarketCap API

Get a free API key.

Replace the API_KEY in the code:

API_KEY = 'your-api-key-here'

Yahoo Finance (No API Key Required)

Uses yfinance with curl-cffi to bypass rate limits.

Ensure yfinance version 0.2.59+ is installed.

### 🏃 Running the Application
```
streamlit run app.py
```

Dashboard opens in your browser at: http://localhost:8501

### 📖 Usage

Cryptocurrency Mode

Select "Crypto Prices" from the sidebar.

Choose your preferred currency (USD, BTC, ETH).

Select cryptocurrencies from the multiselect dropdown.

View price changes by timeframe (1h, 24h, 7d).

Download data as CSV.

Stock Mode

Select "Stock Prices" from the sidebar.

Enter a stock ticker (e.g., AAPL, TSLA, GOOGL).

Choose start and end dates for historical data.

View closing prices and volume charts.

Download historical data as CSV.

### 🛠️ Technologies Used

Streamlit – Web app framework

yfinance – Yahoo Finance API wrapper

pandas – Data manipulation

matplotlib – Visualization

requests – HTTP library

curl-cffi – Rate limit bypass

### ⚙️ Configuration

Rate Limiting:

Crypto API: 20 requests/min

Stock API: 30 requests/min

Caching: Data cached for 5 minutes to improve performance

### 🐛 Troubleshooting

Yahoo Finance Rate Limit Error
```
pip install --upgrade yfinance
pip install curl-cffi
```

Get a free API key from Alpha Vantage

Update the ALPHA_VANTAGE_KEY variable in the code

## 📊 Screenshots

<img width="1891" height="848" alt="image" src="https://github.com/user-attachments/assets/911b52c7-f6e4-40bc-9a89-39b0edcb4ebe" />
<img width="1913" height="870" alt="image" src="https://github.com/user-attachments/assets/2fadaae1-8dd8-4b0d-b633-54d8aca57143" />


### 🤝 Contributing

Fork the repository

Create your feature branch:
```
git checkout -b feature/AmazingFeature
```

Commit changes:
```
git commit -m 'Add AmazingFeature'
```

### Push branch:
```
git push origin feature/AmazingFeature
```

## Open a Pull Request

### 📝 License

MIT License – see LICENSE

### 🙏 Acknowledgments

CoinMarketCap
 – Crypto data

Yahoo Finance
 – Stock data

Streamlit
 – Web framework

yfinance
 community

### 📧 Contact

Your Name – @AnasFareedi_
 – work.anasfareedi@gmail.com

Project Link: https://github.com/anas-fareedi/DashBoard

### 🔄 Updates

v1.0.0 – Initial release

v1.1.0 – Added rate limiting & caching

v1.2.0 – Implemented curl-cffi for Yahoo Finance

### 📈 Future Enhancements

 Portfolio tracking

 Price alerts

 Technical indicators (RSI, MACD)

 Multi-currency support

 Dark mode toggle

 User authentication

### 📦 Quick Start Commands

#### Install dependencies:
```
pip install -r requirements.txt
```

### Run the app:
```
streamlit run app.py
```
