import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
import threading

# Create a global variable to control the connection keeper thread
keep_connection_alive = False
connection_keeper_thread = None

def connection_keeper():
    """Function to keep the MT5 connection alive by periodically pinging the terminal"""
    global keep_connection_alive
    while keep_connection_alive:
        try:
            # Ping the terminal by requesting terminal info
            if mt5.terminal_info() is None:
                st.warning("Connection lost, attempting to reconnect...")
                reconnect_mt5()
            # Sleep for 20 seconds before next ping
            time.sleep(20)
        except Exception as e:
            print(f"Connection keeper error: {e}")
            time.sleep(5)

def ensure_connection():
    """Ensure MT5 connection is active, reconnect if needed"""
    if mt5.terminal_info() is None:
        st.warning("MT5 connection lost. Reconnecting...")
        return reconnect_mt5()
    return True

def reconnect_mt5():
    """Reconnect to MT5"""
    # Close any existing connections
    try:
        mt5.shutdown()
        time.sleep(1)
    except:
        pass
    
    # Initialize MT5
    if mt5.initialize():
        st.success("MT5 reconnected successfully")
        return True
    else:
        st.error(f"MT5 reconnection failed, error: {mt5.last_error()}")
        return False

def get_available_symbols():
    """Get all available symbols from MT5 with connection check"""
    # Check connection first
    if not ensure_connection():
        # Return cached symbols if available
        if 'symbol_categories' in st.session_state:
            return st.session_state['symbol_categories']
        return {}
    
    all_symbols = mt5.symbols_get()
    if all_symbols is None:
        if 'symbol_categories' in st.session_state:
            return st.session_state['symbol_categories']
        return {}
    
    # Extract symbol names
    symbol_names = [s.name for s in all_symbols]
    
    # Create categorized dictionaries
    categories = {
        "Forex": [],
        "Crypto": [],
        "Stocks": [],
        "Commodities": [],
        "Other": []
    }
    
    # Categorize symbols
    for symbol in symbol_names:
        if any(pair in symbol for pair in ["USD", "EUR", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"]) and len(symbol) <= 6:
            categories["Forex"].append(symbol)
        elif any(crypto in symbol for crypto in ["BTC", "ETH", "XRP", "LTC", "BCH", "DOT", "DOGE"]):
            categories["Crypto"].append(symbol)
        elif symbol.startswith("#") or "INDEX" in symbol:
            categories["Indices"].append(symbol)
        elif any(commodity in symbol for commodity in ["GOLD", "XAU", "SILVER", "XAG", "OIL", "BRENT", "NATURAL"]):
            categories["Commodities"].append(symbol)
        elif "." in symbol or symbol.isalpha() and len(symbol) > 3:
            categories["Stocks"].append(symbol)
        else:
            categories["Other"].append(symbol)
    
    # Cache the results in session state
    st.session_state['symbol_categories'] = categories
    return categories

def check_mt5_terminal():
    """Check if MT5 terminal is running and get its path"""
    # Get MT5 terminal path from common installation locations
    possible_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'MetaTrader 5', 'terminal64.exe'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'MetaTrader 5', 'terminal.exe'),
        # Add more common paths if needed
    ]
    
    running = False
    terminal_path = None
    
    try:
        # Check if process is running
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in ['terminal64.exe', 'terminal.exe']:
                running = True
                try:
                    terminal_path = proc.exe()
                except:
                    pass
                break
    except:
        pass
    
    # Check common paths if process not found
    if not running:
        for path in possible_paths:
            if os.path.exists(path):
                terminal_path = path
                break
    
    return {
        'running': running,
        'path': terminal_path
    }

def initialize_mt5():
    """Initialize MT5 connection without login and start connection keeper thread"""
    global keep_connection_alive, connection_keeper_thread
    
    # Make sure any existing connection is closed
    if mt5.terminal_info() is not None:
        mt5.shutdown()
        time.sleep(1)  # Short delay after shutdown
    
    # Initialize MT5 with no timeout (removing timeout restrictions)
    for attempt in range(3):
        if mt5.initialize():  # Removed timeout parameter to avoid automatic disconnection
            # Check if we're already connected to an account
            account_info = mt5.account_info()
            if account_info is not None:
                st.success(f"MT5 initialized successfully. Connected to account: {account_info.login}")
            else:
                st.success("MT5 initialized successfully. No account logged in.")
            
            # Start the connection keeper thread
            keep_connection_alive = True
            if connection_keeper_thread is None or not connection_keeper_thread.is_alive():
                connection_keeper_thread = threading.Thread(target=connection_keeper, daemon=True)
                connection_keeper_thread.start()
            
            return True
        else:
            st.warning(f"MT5 initialization attempt {attempt+1} failed, error: {mt5.last_error()}")
            time.sleep(2)  # Wait before retry
    
    st.error("All initialization attempts failed")
    return False

def download_data(symbol, timeframe, from_date, to_date):
    """Download data from MT5 with connection check"""
    # Ensure connection is active
    if not ensure_connection():
        return None
    
    # Enable symbol for use with multiple attempts
    success = False
    for attempt in range(3):
        if mt5.symbol_select(symbol, True):
            success = True
            break
        else:
            error = mt5.last_error()
            st.warning(f"Symbol selection attempt {attempt+1} failed, error: {error}")
            # If no connection, try to reconnect
            if error[0] == -10004:  # No IPC connection
                reconnect_mt5()
            time.sleep(2)
    
    if not success:
        st.error(f"Failed to select {symbol} after multiple attempts")
        return None
    
    # Download the data with multiple attempts
    rates = None
    for attempt in range(3):
        rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
        if rates is not None and len(rates) > 0:
            break
        else:
            error = mt5.last_error()
            st.warning(f"Data download attempt {attempt+1} failed, error: {error}")
            # If no connection, try to reconnect
            if error and error[0] == -10004:  # No IPC connection
                reconnect_mt5()
            time.sleep(2)
    
    if rates is None or len(rates) == 0:
        st.error("Failed to download data after multiple attempts")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def plot_data(df, symbol):
    """Create a candlestick chart of the data"""
    if df is not None and len(df) > 0:
        fig = go.Figure(data=[go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])
        
        fig.update_layout(
            title=f'{symbol} Price Chart',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False
        )
        
        return fig
    return None

def disconnect_mt5():
    """Properly disconnect from MT5"""
    global keep_connection_alive, connection_keeper_thread
    
    # Stop the connection keeper thread
    keep_connection_alive = False
    if connection_keeper_thread and connection_keeper_thread.is_alive():
        connection_keeper_thread.join(timeout=1)
    
    # Shutdown MT5
    try:
        mt5.shutdown()
        st.session_state['connected'] = False
        st.success("Disconnected from MT5")
        return True
    except Exception as e:
        st.error(f"Error disconnecting: {e}")
        return False

def main():
    st.set_page_config(page_title="MT5 Data Downloader", layout="wide")
    
    # Set up session state variables if they don't exist
    if 'connected' not in st.session_state:
        st.session_state['connected'] = False
    
    st.title("MetaTrader 5 Data Downloader")
    st.markdown("Download historical financial data from MetaTrader 5")
    
    # MT5 Connection Section
    st.header("Connection Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Check MT5 terminal status
        terminal_status = check_mt5_terminal()
        if terminal_status['running']:
            st.info("✅ MT5 terminal is running")
        else:
            if terminal_status['path']:
                st.warning("❌ MT5 terminal is not running. Please start it first.")
                if st.button("Launch MT5"):
                    try:
                        import subprocess
                        subprocess.Popen([terminal_status['path']])
                        st.success("MT5 launch requested")
                    except Exception as e:
                        st.error(f"Failed to start MT5: {e}")
            else:
                st.error("❌ MT5 terminal not found. Please install or start MT5 manually before connecting.")
    
    with col2:
        # Connection button layout
        if not st.session_state['connected']:
            if st.button("Connect to MT5", use_container_width=True):
                if initialize_mt5():
                    st.session_state['connected'] = True
                    # Load symbols right after connection
                    get_available_symbols()
                else:
                    st.session_state['connected'] = False
        else:
            if st.button("Disconnect from MT5", use_container_width=True):
                disconnect_mt5()
    
    # Connection status
    if not st.session_state['connected']:
        st.info("Click 'Connect to MT5' to start")
    else:
        st.success("Connected to MT5")
        
        # Show account info if available
        account_info = mt5.account_info()
        if account_info is not None:
            st.info(f"Connected to account: {account_info.login} (Server: {account_info.server})")
            # Additional account info if needed
            with st.expander("Account Details"):
                st.write(f"Balance: {account_info.balance}")
                st.write(f"Equity: {account_info.equity}")
                st.write(f"Margin: {account_info.margin}")
                st.write(f"Free Margin: {account_info.margin_free}")
                st.write(f"Leverage: 1:{account_info.leverage}")
        else:
            st.info("Connected to MT5 without an account. Some data may be limited.")
        
        # Connection keeper status
        with st.expander("Connection Status"):
            st.write("Connection monitor is active")
            if st.button("Manual Reconnect"):
                reconnect_mt5()
    
    # If connected, show data download options
    if st.session_state.get('connected', False):
        st.header("Data Download Options")
        
        # Get available symbols and categorize them
        symbol_categories = get_available_symbols()
        
        # Symbol Selection Section
        st.subheader("Symbol Selection")
        
        # Create tabs for different categories
        tabs = st.tabs(["Forex", "Crypto", "Stocks", "Indices", "Commodities", "Other", "Custom"])
        
        # Add symbols to each tab
        for i, category in enumerate(["Forex", "Crypto", "Stocks", "Indices", "Commodities", "Other"]):
            with tabs[i]:
                if symbol_categories.get(category, []):
                    symbol_choice = st.selectbox(
                        f"Select {category} Symbol", 
                        options=sorted(symbol_categories[category]),
                        key=f"select_{category}"
                    )
                    if st.button(f"Use {symbol_choice}", key=f"use_{category}"):
                        st.session_state['selected_symbol'] = symbol_choice
                else:
                    st.info(f"No {category.lower()} symbols available")
        
        # Custom symbol entry
        with tabs[6]:
            custom_symbol = st.text_input("Enter Symbol Manually")
            if st.button("Use Custom Symbol"):
                st.session_state['selected_symbol'] = custom_symbol
        
        # Show selected symbol
        if 'selected_symbol' in st.session_state:
            st.info(f"Selected Symbol: {st.session_state['selected_symbol']}")
            
            # Timeframe Selection
            st.subheader("Timeframe Selection")
            timeframe_options = {
                "1 Minute": mt5.TIMEFRAME_M1,
                "5 Minutes": mt5.TIMEFRAME_M5,
                "15 Minutes": mt5.TIMEFRAME_M15,
                "30 Minutes": mt5.TIMEFRAME_M30,
                "1 Hour": mt5.TIMEFRAME_H1,
                "4 Hours": mt5.TIMEFRAME_H4,
                "Daily": mt5.TIMEFRAME_D1,
                "Weekly": mt5.TIMEFRAME_W1,
                "Monthly": mt5.TIMEFRAME_MN1
            }
            selected_timeframe = st.selectbox("Select Timeframe", options=list(timeframe_options.keys()))
            timeframe_value = timeframe_options[selected_timeframe]
            
            # Date Range Selection
            st.subheader("Date Range")
            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input("From Date", datetime.now() - timedelta(days=30))
            with col2:
                to_date = st.date_input("To Date", datetime.now())
            
            # Convert dates to datetime
            from_datetime = datetime.combine(from_date, datetime.min.time())
            to_datetime = datetime.combine(to_date, datetime.min.time())
            
            # Download Button
            if st.button("Download Data"):
                symbol = st.session_state['selected_symbol']
                
                with st.spinner(f"Downloading {symbol} data..."):
                    df = download_data(symbol, timeframe_value, from_datetime, to_datetime)
                    
                    if df is not None and len(df) > 0:
                        st.session_state['data'] = df
                        st.session_state['symbol'] = symbol
                        st.session_state['timeframe'] = selected_timeframe
                        
                        # Save as CSV
                        csv_filename = f"{symbol}_{selected_timeframe.replace(' ', '_')}_{from_date}_to_{to_date}.csv"
                        df.to_csv(csv_filename, index=False)
                        
                        st.success(f"Downloaded {len(df)} bars of data")
                        
                        # Provide download link
                        st.download_button(
                            label="Download CSV",
                            data=df.to_csv(index=False),
                            file_name=csv_filename,
                            mime="text/csv"
                        )
                    else:
                        st.error("Failed to download data")
        
        # Display data if available
        if 'data' in st.session_state:
            st.header(f"Data Preview: {st.session_state['symbol']} ({st.session_state['timeframe']})")
            st.dataframe(st.session_state['data'].head(10))
            
            # Plot data
            st.header("Price Chart")
            fig = plot_data(st.session_state['data'], st.session_state['symbol'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Display troubleshooting information at the bottom if not connected
    if not st.session_state.get('connected', False):
        st.header("Troubleshooting")
        st.markdown("""
        ### Common Issues:
        
        1. **MT5 Not Running**: Ensure MetaTrader 5 is open before connecting
        2. **MT5 Permissions**: Make sure MT5 allows API connections (Tools > Options > Expert Advisors > Allow WebRequest)
        3. **Limited Data**: Without account login, some brokers limit available data
        4. **Firewall Blocking**: Check if your firewall is blocking connections
        5. **Antivirus Interference**: Temporarily disable antivirus to test connection
        
        ### Important Notes:
        
        - This application connects to your local MT5 terminal
        - You can download data without logging in, but symbol availability may be limited
        - For full access to all symbols, having a demo or real account logged in within MT5 is recommended
        """)
    
    # Cleanup connection when app closes
    if hasattr(st, 'session_state') and '_is_running' in st.session_state:
        if not st.session_state['_is_running']:
            disconnect_mt5()

if __name__ == "__main__":
    # Mark that the app is running
    st.session_state['_is_running'] = True
    main()