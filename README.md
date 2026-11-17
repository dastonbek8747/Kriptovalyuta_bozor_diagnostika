# Crypto Market Dashboard

> A Streamlit dashboard that analyses crypto market data across several exchanges using ccxt and Plotly.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)


## Features

- Live market data from multiple exchanges through ccxt.
- Interactive Plotly charts.
- Compare price action across symbols.
- Read-only: it never places orders.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Market data | ccxt |
| Charts | Plotly |
| Data | pandas |

## Quick Start

```bash
git clone https://github.com/dastonbek8747/crypto-market-dashboard.git
cd crypto-market-dashboard
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

## Environment variables

Public market data needs no key. Add any optional key to `.env` if you use an exchange that requires one.

## License

MIT © 2026 Doston Sultonov.
