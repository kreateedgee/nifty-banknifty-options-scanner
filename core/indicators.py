"""Technical indicators and candle-pattern helpers; expects OHLCV columns."""
from __future__ import annotations
import numpy as np
import pandas as pd

REQUIRED = {"open", "high", "low", "close", "volume"}

def enrich_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {', '.join(sorted(missing))}")
    df = frame.copy().sort_index()
    close, high, low, volume = df.close, df.high, df.low, df.volume
    df["ema_9"] = close.ewm(span=9, adjust=False).mean()
    df["ema_21"] = close.ewm(span=21, adjust=False).mean()
    df["ema_50"] = close.ewm(span=50, adjust=False).mean()
    delta = close.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi_14"] = (100 - 100 / (1 + rs)).fillna(50)
    ema12, ema26 = close.ewm(span=12, adjust=False).mean(), close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df.macd.ewm(span=9, adjust=False).mean()
    tr = pd.concat([(high-low), (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    typical = (high + low + close) / 3
    if isinstance(df.index, pd.DatetimeIndex):
        session = pd.Series(df.index.date, index=df.index)
        pv = typical * volume
        df["vwap"] = pv.groupby(session).cumsum() / volume.groupby(session).cumsum().replace(0, np.nan)
    else:
        df["vwap"] = (typical * volume).cumsum() / volume.cumsum().replace(0, np.nan)
    df["volume_sma_20"] = volume.rolling(20, min_periods=1).mean()
    df["volume_ratio"] = volume / df.volume_sma_20.replace(0, np.nan)
    body = (close - df.open).abs()
    candle_range = (high - low).replace(0, np.nan)
    df["bullish_engulfing"] = ((close > df.open) & (df.close.shift(1) < df.open.shift(1)) & (df.open <= df.close.shift(1)) & (close >= df.open.shift(1)))
    df["bearish_engulfing"] = ((close < df.open) & (df.close.shift(1) > df.open.shift(1)) & (df.open >= df.close.shift(1)) & (close <= df.open.shift(1)))
    df["doji"] = (body / candle_range) <= 0.10
    df["body_ratio"] = (body / candle_range).fillna(0)
    return df.replace([np.inf, -np.inf], np.nan)
