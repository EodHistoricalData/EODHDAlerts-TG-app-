# strategy.py

import pandas as pd


class SMACrossoverStrategy:
    def __init__(self, short_window: int, long_window: int):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        close_field = "close"
        if "adjusted_close" in data.columns:
            close_field = "adjusted_close"

        data = data.copy()
        data[f"sma{self.short_window}"] = (
            data[close_field].rolling(window=self.short_window, min_periods=1).mean()
        )
        data[f"sma{self.long_window}"] = (
            data[close_field].rolling(window=self.long_window, min_periods=1).mean()
        )
        data["signal"] = 0
        data.loc[data[f"sma{self.short_window}"] > data[f"sma{self.long_window}"], "signal"] = 1
        data.loc[data[f"sma{self.short_window}"] < data[f"sma{self.long_window}"], "signal"] = -1
        data["position"] = data["signal"].diff()
        
        return data
