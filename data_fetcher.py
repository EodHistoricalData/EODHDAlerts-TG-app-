# data_fetcher.py

import pandas as pd
from eodhd import APIClient
from config import EODHD_API_TOKEN, DEFAULT_SYMBOL, DEFAULT_INTERVAL
from datetime import datetime, timedelta


class DataFetcher:
    def __init__(self, symbol: str = DEFAULT_SYMBOL, interval: str = DEFAULT_INTERVAL):
        self.api = APIClient(EODHD_API_TOKEN)
        self.symbol = symbol
        self.interval = interval

    def fetch_ohlc(self) -> pd.DataFrame:
        if self.interval in ["d", "w", "m"]:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=365)

            data = self.api.get_eod_historical_stock_market_data(
                symbol=self.symbol,
                period=self.interval,
                from_date=start_time.strftime("%Y-%m-%d"),
                to_date=end_time.strftime("%Y-%m-%d"),
                order="a",
            )
        elif self.interval in ["1m", "5m", "h"]:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=14)

            data = self.api.get_intraday_historical_data(
                symbol=self.symbol,
                interval=self.interval,
                from_unix_time=start_time.timestamp(),
                to_unix_time=end_time.timestamp(),
            )
        else:
            raise ValueError("Invalid interval (1m, 5m, 1h, d, w, m)")

        df = pd.DataFrame(data)
        df.dropna(inplace=True)
        df.drop(columns=["timestamp", "gmtoffset"], errors="ignore", inplace=True)

        return df

    def fetch_price(self) -> float:
        data = self.api.get_live_stock_prices(ticker=self.symbol)
        if len(data) == 0 or "close" not in data:
            return None
        return data["close"]
