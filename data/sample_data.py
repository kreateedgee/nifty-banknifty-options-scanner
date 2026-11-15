"""Deterministic sample candles for dashboard preview; not live market data."""
import numpy as np
import pandas as pd

def sample_ohlcv(seed: int = 7, periods: int = 180, start: float = 24000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(end=pd.Timestamp.now().floor("5min"), periods=periods, freq="5min")
    drift = np.linspace(0, 45, periods)
    close = start + drift + np.cumsum(rng.normal(0, 13, periods))
    open_ = np.r_[close[0] - rng.normal(0, 5), close[:-1]]
    high = np.maximum(open_, close) + rng.uniform(2, 12, periods)
    low = np.minimum(open_, close) - rng.uniform(2, 12, periods)
    volume = rng.integers(1000, 9000, periods)
    return pd.DataFrame({"open":open_, "high":high, "low":low, "close":close, "volume":volume}, index=idx)
