# test_datafetcher.py

import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_fetcher import DataFetcher

fetcher = DataFetcher("AAPL.MX", "d")
# fetcher = DataFetcher("BTC-USD.CC", "5m")
# data = fetcher.fetch_ohlc()
data = fetcher.fetch_price()
print(data)
