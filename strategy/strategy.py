# strategy.py

from abc import ABC, abstractmethod
import pandas as pd
import pandas_ta as ta


class Strategy(ABC):
    """Base interface for all trading strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Takes OHLC DataFrame and returns it with `signal` + `position` columns."""


class SmaCrossoverStrategy(Strategy):
    """Simple Moving Average crossover."""

    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[f"sma_{self.short_window}"] = (
            df["close"].rolling(window=self.short_window, min_periods=1).mean()
        )
        df[f"sma_{self.long_window}"] = (
            df["close"].rolling(window=self.long_window, min_periods=1).mean()
        )
        df["signal"] = 0
        df.loc[
            df[f"sma_{self.short_window}"] > df[f"sma_{self.long_window}"], "signal"
        ] = 1
        df.loc[
            df[f"sma_{self.short_window}"] < df[f"sma_{self.long_window}"], "signal"
        ] = -1
        df["position"] = df["signal"].diff().fillna(0)
        return df


class EmaCrossoverStrategy(Strategy):
    """Exponential Moving Average crossover."""

    def __init__(self, short_span: int = 12, long_span: int = 26):
        self.short_span = short_span
        self.long_span = long_span

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[f"ema_{self.short_span}"] = ta.ema(df["close"], length=self.short_span)
        df[f"ema_{self.long_span}"] = ta.ema(df["close"], length=self.long_span)
        df["signal"] = 0
        df.loc[df[f"ema_{self.short_span}"] > df[f"ema_{self.long_span}"], "signal"] = 1
        df.loc[df[f"ema_{self.short_span}"] < df[f"ema_{self.long_span}"], "signal"] = (
            -1
        )
        df["position"] = df["signal"].diff().fillna(0)
        return df


class RsiStrategy(Strategy):
    """Relative Strength Index-based strategy."""

    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df["rsi"] = ta.rsi(df["close"], length=self.period)
        df["signal"] = 0
        df.loc[df["rsi"] < self.oversold, "signal"] = 1
        df.loc[df["rsi"] > self.overbought, "signal"] = -1
        df["position"] = df["signal"].diff().fillna(0)
        return df


class MacdStrategy(Strategy):
    """Moving Average Convergence Divergence."""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        macd = ta.macd(df["close"], fast=self.fast, slow=self.slow, signal=self.signal)
        df = df.join(macd)
        df["signal"] = 0
        df.loc[df["MACD_12_26_9"] > df["MACDs_12_26_9"], "signal"] = 1
        df.loc[df["MACD_12_26_9"] < df["MACDs_12_26_9"], "signal"] = -1
        df["position"] = df["signal"].diff().fillna(0)
        return df


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands breakout."""

    def __init__(self, length: int = 20, std: int = 2):
        self.length = length
        self.std = std

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        bb = ta.bbands(df["close"], length=self.length, std=self.std)
        df = df.join(bb)
        df["signal"] = 0
        df.loc[df["close"] > df["BBU_20_2.0"], "signal"] = 1
        df.loc[df["close"] < df["BBL_20_2.0"], "signal"] = -1
        df["position"] = df["signal"].diff().fillna(0)
        return df


class StrategyFactory:
    """Creates strategies by name and lists available options."""

    _strategies = {
        "sma": SmaCrossoverStrategy,
        "ema": EmaCrossoverStrategy,
        "rsi": RsiStrategy,
        "macd": MacdStrategy,
        "bbands": BollingerBandsStrategy,
    }

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(cls, name: str, **kwargs) -> Strategy:
        name = name.lower()
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return cls._strategies[name](**kwargs)


class StrategyFactory:
    """Creates strategies by name and lists available options."""

    _strategies = {
        "sma": SmaCrossoverStrategy,
        "ema": EmaCrossoverStrategy,
        "rsi": RsiStrategy,
        "macd": MacdStrategy,
        "bbands": BollingerBandsStrategy,
    }

    @classmethod
    def list_strategies(cls) -> list[str]:
        return list(cls._strategies.keys())

    @classmethod
    def create_strategy(cls, name: str, **kwargs) -> Strategy:
        name = name.lower()
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return cls._strategies[name](**kwargs)
