# data_fetcher.py

import pandas as pd
from eodhd import APIClient
from config import EODHD_API_TOKEN, DEFAULT_SYMBOL, DEFAULT_INTERVAL
from datetime import datetime, timedelta
from typing import Optional
import pytz


class DataFetcher:
    def __init__(self, symbol: str = DEFAULT_SYMBOL, interval: str = DEFAULT_INTERVAL):
        self.api = APIClient(EODHD_API_TOKEN)
        self.symbol = symbol
        self.interval = interval

    def fetch_ohlc(self) -> pd.DataFrame:
        now = datetime.now(pytz.UTC)

        if self.interval in ["d", "w", "m"]:
            start = now - timedelta(days=365)
            data = self.api.get_eod_historical_stock_market_data(
                symbol=self.symbol,
                period=self.interval,
                from_date=start.strftime("%Y-%m-%d"),
                to_date=now.strftime("%Y-%m-%d"),
                order="a",
            )
        elif self.interval in ["1m", "5m", "h"]:
            start = now - timedelta(days=14)
            data = self.api.get_intraday_historical_data(
                symbol=self.symbol,
                interval=self.interval,
                from_unix_time=start.timestamp(),
                to_unix_time=now.timestamp(),
            )
        else:
            raise ValueError("Invalid interval (1m, 5m, h, d, w, m)")

        df = pd.DataFrame(data)
        df.dropna(inplace=True)
        df.drop(columns=["timestamp", "gmtoffset"], errors="ignore", inplace=True)

        # Parse timestamp into datetime
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], utc=True)
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

        return df

    def fetch_price(self) -> Optional[float]:
        data = self.api.get_live_stock_prices(ticker=self.symbol)
        if not data or "close" not in data:
            return None
        return data["close"]
