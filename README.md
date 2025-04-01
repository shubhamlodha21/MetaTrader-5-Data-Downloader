# MetaTrader-5-Data-Downloader
Download historical financial data from MetaTrader 5

## Overview
The MetaTrader 5 Data Downloader is a Streamlit-based application that allows users to download historical financial data directly from their MetaTrader 5 terminal. It provides an easy-to-use interface for selecting symbols, timeframes, and date ranges to fetch OHLC (Open, High, Low, Close) data for financial instruments.

## Features
- Connect to a locally running MetaTrader 5 terminal
- Browse available financial symbols by category (Forex, Crypto, Stocks, etc.)
- Select custom timeframes (1m, 5m, 15m, 30m, 1h, 4h, D1, W1, MN)
- Specify custom date ranges for data download
- Export data to CSV format
- Visualize price data with interactive candlestick charts
- Automatic reconnection to MT5 if connection is lost
- Connection status monitoring

## Requirements
- Python 3.7+
- MetaTrader 5 terminal installed and running locally
- MetaTrader 5 configured to allow API connections
- Python packages (see requirements.txt)

## Important Limitations
⚠️ **This is a LOCAL ONLY application** ⚠️

This application has several important limitations you should understand:

1. **Local Connection Only**: The app connects to a MetaTrader 5 terminal running on the same computer. It cannot connect to remote MT5 instances over the internet.

2. **Personal Use**: This app is designed for personal use on your own computer. It cannot be deployed as a public web service that others can use to download MT5 data without having their own installation.

3. **MT5 Must Be Running**: MetaTrader 5 must be installed and running on your computer before launching the app.

4. **Broker Limitations**: The available symbols and historical data depend on what your broker provides through MT5.

5. **Account Requirements**: While you can connect without logging into an account, some brokers limit available data for unauthenticated connections.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/mt5-data-downloader.git
cd mt5-data-downloader
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure MetaTrader 5
- Open MetaTrader 5
- Go to Tools > Options > Expert Advisors
- Enable "Allow WebRequest for listed URL"
- Make sure "Allow DLL imports" is enabled

## Usage

### 1. Start MetaTrader 5
Make sure your MetaTrader 5 terminal is running before starting the app.

### 2. Launch the application
```bash
streamlit run app.py
```

### 3. Connect to MT5
- Click the "Connect to MT5" button in the application
- If successful, you'll see available symbols and categories

### 4. Download Data
- Select a symbol from one of the category tabs (or enter a custom symbol)
- Choose a timeframe
- Select date range
- Click "Download Data"
- Use the "Download CSV" button to save the data

## Sharing Options

Since this app connects to a local MT5 instance, there are limitations on how it can be shared:

### Option 1: Share the code for others to run locally
- Others will need to install MT5 and this app on their computers
- They must run Streamlit and have MT5 running locally

### Option 2: Consider a client-server architecture (advanced)
For a multi-user solution, you would need to:
1. Set up a dedicated server running MT5
2. Create a data collection service that stores market data in a database
3. Build an API to serve this data
4. Modify the Streamlit app to fetch from your API instead of connecting directly to MT5

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This software is for educational and personal use only. Trading financial instruments carries risk. This tool does not provide investment advice. Past performance is not indicative of future results.
