# 📊 MetaTrader-5-Data-Downloader
## 🚀 Download historical financial data from MetaTrader 5

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.0+-red.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 🌟 Overview
The MetaTrader 5 Data Downloader is a Streamlit-based application that allows users to download historical financial data directly from their MetaTrader 5 terminal. It provides an easy-to-use interface for selecting symbols, timeframes, and date ranges to fetch OHLC (Open, High, Low, Close) data for financial instruments.

## ✨ Features
* 🔌 Connect to a locally running MetaTrader 5 terminal
* 🔍 Browse available financial symbols by category (Forex, Crypto, Stocks, etc.)
* ⏱️ Select custom timeframes (1m, 5m, 15m, 30m, 1h, 4h, D1, W1, MN)
* 📅 Specify custom date ranges for data download
* 📥 Export data to CSV, Excel, or JSON formats
* 📈 Visualize price data with interactive candlestick charts
* 🔄 Automatic reconnection to MT5 if connection is lost
* 📡 Connection status monitoring
* 📊 Technical indicator calculation (RSI, MACD, Bollinger Bands)
* 🔔 Data integrity validation
* 🌙 Dark/Light mode toggle

## 🛠️ Requirements
* Python 3.7+
* MetaTrader 5 terminal installed and running locally
* MetaTrader 5 configured to allow API connections
* Python packages (see requirements.txt)

## ⚠️ Important Limitations
**This is a LOCAL ONLY application** ⚠️

This application has several important limitations you should understand:

1. **🖥️ Local Connection Only**: The app connects to a MetaTrader 5 terminal running on the same computer. It cannot connect to remote MT5 instances over the internet.

2. **👤 Personal Use**: This app is designed for personal use on your own computer. It cannot be deployed as a public web service that others can use to download MT5 data without having their own installation.

3. **🏃‍♂️ MT5 Must Be Running**: MetaTrader 5 must be installed and running on your computer before launching the app.

4. **🏢 Broker Limitations**: The available symbols and historical data depend on what your broker provides through MT5.

5. **🔑 Account Requirements**: While you can connect without logging into an account, some brokers limit available data for unauthenticated connections.

## 📥 Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/mt5-data-downloader.git
cd mt5-data-downloader
```

2. Create a virtual environment (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure MetaTrader 5
* Open MetaTrader 5
* Go to Tools > Options > Expert Advisors
* Enable "Allow WebRequest for listed URL"
* Make sure "Allow DLL imports" is enabled

## 🚀 Usage

1. **Start MetaTrader 5**
   * Make sure your MetaTrader 5 terminal is running before starting the app.

2. **Launch the application**
```bash
streamlit run app.py
```

3. **Connect to MT5**
   * Click the "Connect to MT5" button in the application
   * If successful, you'll see available symbols and categories

4. **Download Data**
   * Select a symbol from one of the category tabs (or enter a custom symbol)
   * Choose a timeframe
   * Select date range
   * Click "Download Data"
   * Use the "Export" dropdown to save the data in your preferred format

## 📊 Data Analysis Features

* **📉 Candlestick Charts**: Visualize price action with interactive charts
* **📏 Technical Indicators**: Calculate and display common indicators
* **📰 Economic Calendar Integration**: View relevant economic events
* **📊 Basic Statistics**: View summary statistics for selected data
* **📅 Gap Analysis**: Identify and highlight data gaps

## 🔄 Workflow Example

```python
# Example code showing how the app connects to MT5
import MetaTrader5 as mt5

def connect_to_mt5():
    if not mt5.initialize():
        return False, f"Failed to initialize MT5: {mt5.last_error()}"
    
    # Check connection
    if not mt5.terminal_info():
        mt5.shutdown()
        return False, "MT5 terminal not connected"
    
    return True, "Connected successfully"

# Example of data retrieval
def get_historical_data(symbol, timeframe, from_date, to_date):
    # Convert timeframe string to MT5 timeframe constant
    tf_map = {
        "1m": mt5.TIMEFRAME_M1,
        "5m": mt5.TIMEFRAME_M5,
        "15m": mt5.TIMEFRAME_M15,
        # etc.
    }
    
    # Get data
    rates = mt5.copy_rates_range(symbol, tf_map[timeframe], from_date, to_date)
    
    # Process and return as pandas DataFrame
    # ...
```

## 🔒 Privacy & Security

* All data processing happens locally on your machine
* No data is sent to external servers
* No login credentials are stored by the application
* MT5 connection uses native MetaTrader API

## 🖥️ Sharing Options

Since this app connects to a local MT5 instance, there are limitations on how it can be shared:

### Option 1: Share the code for others to run locally
* Others will need to install MT5 and this app on their computers
* They must run Streamlit and have MT5 running locally

### Option 2: Consider a client-server architecture (advanced)
For a multi-user solution, you would need to:
1. Set up a dedicated server running MT5
2. Create a data collection service that stores market data in a database
3. Build an API to serve this data
4. Modify the Streamlit app to fetch from your API instead of connecting directly to MT5

## 📋 Advanced Configuration

Create a `config.json` file to customize behavior:
```json
{
  "default_timeframe": "1h",
  "default_symbols": ["EURUSD", "BTCUSD", "AAPL"],
  "chart_theme": "dark",
  "max_bars": 10000,
  "cache_expiry": 3600,
  "indicators": {
    "enable_default": ["MA", "RSI"],
    "ma_periods": [9, 20, 50, 200]
  }
}
```

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| MT5 connection fails | Ensure MT5 is running and properly configured |
| Symbol not found | Check if your broker provides the requested symbol |
| Data gaps | Some timeframes may have missing bars during off-market hours |
| Performance issues | Try reducing the date range or number of indicators |

## 🛣️ Roadmap
* 📱 Mobile-responsive UI
* 🔄 Real-time data streaming options
* 📤 Direct export to trading platforms
* 🔍 Advanced pattern recognition
* 📑 Multiple symbol comparison
* 🤖 Strategy backtesting integration
* 🌐 Custom API for saved datasets
* 🔐 Enhanced security options

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer
This software is for educational and personal use only. Trading financial instruments carries risk. This tool does not provide investment advice. Past performance is not indicative of future results.

## 📞 Support
For issues or questions:
* Email: [shubhamlodha2111@gmail.com](mailto:shubhamlodha2111@gmail.com)

## 👏 Acknowledgements
* [MetaTrader 5](https://www.metatrader5.com/) for providing the API
* [Streamlit](https://streamlit.io/) for the web app framework
* All open-source contributors