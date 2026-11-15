import streamlit as st
import plotly.graph_objects as go
from core.scanner import analyse
from core.indicators import enrich_ohlcv
from data.sample_data import sample_ohlcv

st.set_page_config(page_title="Index Options Scanner", page_icon="📈", layout="wide")
st.title("NIFTY & BANK NIFTY Options Scanner")
st.caption("Research dashboard | Sample data only | No order execution")
st.warning("DEMO MODE: prices are generated sample data, not live market prices. Do not use them to make trades.")

with st.sidebar:
    st.header("Scanner settings")
    symbol = st.selectbox("Index", ["NIFTY", "BANKNIFTY"])
    timeframe = st.selectbox("Timeframe", ["5-minute", "15-minute"])
    st.divider()
    st.info("Broker feeds are not connected in this version.")

raw = sample_ohlcv(seed=7 if symbol == "NIFTY" else 19,
                   start=24000 if symbol == "NIFTY" else 52000)
if timeframe == "15-minute":
    raw = raw.resample("15min").agg({
        "open": "first", "high": "max", "low": "min",
        "close": "last", "volume": "sum"
    }).dropna()

df = enrich_ohlcv(raw)
signal = analyse(raw, symbol, timeframe)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Research signal", signal["signal"])
c2.metric("Signal score", str(signal["score"]) + "/7")
c3.metric("RSI (14)", signal.get("rsi", "—"))
c4.metric("Underlying reference", f'{signal.get("underlying_reference", 0):,.2f}')

st.subheader("Candlestick chart and indicators")
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index, open=df["open"], high=df["high"], low=df["low"],
    close=df["close"], name="Price"
))
for column in ["ema_9", "ema_21", "ema_50", "vwap"]:
    fig.add_trace(go.Scatter(x=df.index, y=df[column], mode="lines", name=column.upper()))
fig.update_layout(height=560, xaxis_rangeslider_visible=False, legend_orientation="h")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Why this signal?")
    st.write("Instrument: " + symbol + " | Timeframe: " + timeframe)
    for reason in signal["reasons"]:
        st.write("- " + reason)
with right:
    st.subheader("Underlying reference levels")
    st.write("Invalidation: " + str(signal.get("invalidation") or "—"))
    st.write("Target 1: " + str(signal.get("target_1") or "—"))
    st.write("Target 2: " + str(signal.get("target_2") or "—"))
    st.caption(signal.get("warning", ""))

st.subheader("Latest candle data")
st.dataframe(df[["open", "high", "low", "close", "volume",
                 "ema_9", "ema_21", "rsi_14", "vwap", "volume_ratio"]].tail(20),
             use_container_width=True)
st.caption("This demo does not connect to Angel One or Zerodha, analyse option-chain Greeks/OI, send Telegram alerts, or place orders.")
