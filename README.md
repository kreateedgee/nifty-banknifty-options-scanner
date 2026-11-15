# NIFTY & BANK NIFTY Options Scanner

Intraday analysis and alerting dashboard for NIFTY and BANK NIFTY options, designed for 5-minute and 15-minute chart analysis. Research signals: BULLISH CE / BEARISH PE / WAIT.

> Important: This is decision-support software, not investment advice. Options are high risk and signals are not guaranteed to be profitable. Automatic order placement is intentionally not implemented.

## Initial capabilities
- Streamlit dashboard with sample-data mode.
- EMA 9/21/50, RSI, MACD, ATR, VWAP and volume ratio.
- Basic candle-pattern detection and transparent trend/momentum scoring.
- CE / PE / WAIT candidate framework with underlying reference, invalidation and indicative targets.
- Broker adapters kept separate from signal generation.
- No credentials stored in source code.

## Quick start (Windows)
1. Install Python 3.11 or newer.
2. Open a terminal in this folder.
3. Create an environment: py -m venv .venv
4. Activate it: .venv\\Scripts\\activate
5. Install packages: pip install -r requirements.txt
6. Copy .env.example to .env. Add credentials locally only after broker integration is configured.
7. Run: streamlit run app.py

The first version is designed to run with generated sample candles so the dashboard can be explored without broker credentials.

## Broker integration status
Angel One SmartAPI and Zerodha Kite Connect are planned adapters. Keep credentials in local environment variables; never commit .env or API secrets.

## Safety and validation
- Alerts only; no order execution.
- Treat signals as candidates, not instructions to trade.
- Validate option bid/ask spread, volume, open interest, implied volatility, Greeks, expiry and premium behaviour before considering a trade.
- Backtest with brokerage, taxes, slippage, liquidity and expiry effects.
- Paper trade before relying on live market data.

## Project layout
- app.py — Streamlit dashboard
- core/indicators.py — technical indicators and candle patterns
- core/scanner.py — CE / PE / WAIT scoring
- data/sample_data.py — sample OHLCV generator
- brokers/README.md — broker integration notes
