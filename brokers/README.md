# Broker adapters (planned)

The dashboard currently uses sample OHLCV data. Angel One SmartAPI and Zerodha Kite Connect adapters will be implemented after account/API setup is confirmed.

- Store credentials only in local environment variables or a secret manager.
- Never paste secrets into chat or commit them to GitHub.
- Use official broker SDKs/APIs and comply with broker terms.
- Keep the scanner analysis/alert-only; do not add order-placement calls.
