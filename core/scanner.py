"""Transparent rule-based CE/PE/WAIT candidate scoring."""
from __future__ import annotations
import pandas as pd
from core.indicators import enrich_ohlcv

def analyse(frame: pd.DataFrame, symbol: str, timeframe: str) -> dict:
    df = enrich_ohlcv(frame).dropna(subset=["ema_21", "atr_14"])
    if len(df) < 25:
        return {"symbol": symbol, "timeframe": timeframe, "signal": "WAIT", "score": 0,
                "reasons": ["At least 25 candles are required for this initial scan."]}
    last, prev = df.iloc[-1], df.iloc[-2]
    bull, bear, reasons = 0, 0, []
    if last.close > last.ema_9 > last.ema_21 > last.ema_50:
        bull += 2; reasons.append("Bullish EMA alignment (9 > 21 > 50)")
    elif last.close < last.ema_9 < last.ema_21 < last.ema_50:
        bear += 2; reasons.append("Bearish EMA alignment (9 < 21 < 50)")
    if last.close > last.vwap:
        bull += 1; reasons.append("Price above session VWAP")
    elif last.close < last.vwap:
        bear += 1; reasons.append("Price below session VWAP")
    if last.rsi_14 >= 55:
        bull += 1; reasons.append(f"RSI momentum positive ({last.rsi_14:.1f})")
    elif last.rsi_14 <= 45:
        bear += 1; reasons.append(f"RSI momentum negative ({last.rsi_14:.1f})")
    if last.macd > last.macd_signal and prev.macd <= prev.macd_signal:
        bull += 1; reasons.append("MACD bullish crossover")
    elif last.macd < last.macd_signal and prev.macd >= prev.macd_signal:
        bear += 1; reasons.append("MACD bearish crossover")
    if last.volume_ratio >= 1.5:
        if last.close > last.open: bull += 1
        elif last.close < last.open: bear += 1
        reasons.append(f"Volume expansion ({last.volume_ratio:.1f}x 20-candle average)")
    if bool(last.bullish_engulfing):
        bull += 1; reasons.append("Bullish engulfing candle")
    if bool(last.bearish_engulfing):
        bear += 1; reasons.append("Bearish engulfing candle")
    score = max(bull, bear)
    signal = "BULLISH CE" if bull >= 4 and bull >= bear + 2 else "BEARISH PE" if bear >= 4 and bear >= bull + 2 else "WAIT"
    direction = 1 if signal == "BULLISH CE" else -1 if signal == "BEARISH PE" else 0
    entry, atr = float(last.close), float(last.atr_14)
    return {"symbol": symbol, "timeframe": timeframe, "signal": signal,
            "score": int(score), "confidence": round(min(score / 7, 1) * 100),
            "underlying_reference": round(entry, 2),
            "invalidation": round(entry - direction * atr, 2) if direction else None,
            "target_1": round(entry + direction * atr * 1.5, 2) if direction else None,
            "target_2": round(entry + direction * atr * 2, 2) if direction else None,
            "rsi": round(float(last.rsi_14), 1), "atr": round(atr, 2),
            "reasons": reasons or ["No clear directional confirmation."],
            "warning": "Underlying-index levels only; not option-premium entry/SL/targets. Confirm option-chain liquidity, spread, IV, Greeks and premium movement."}
