# Binance Futures Testnet Trading Bot

## Overview

This project is a simple Python-based CLI trading bot that interacts with the
Binance Futures Testnet (USDT-M). It allows users to place MARKET and LIMIT
orders using Binance's test environment.

The application demonstrates:

- API interaction with Binance Futures Testnet
- Clean project structure
- CLI-based user input
- Logging of requests, responses, and errors
- Input validation and error handling

This project is intended as a simplified trading bot for demonstration and
technical evaluation purposes.

---

## Project Structure

```
trading_bot/
│
├── bot/
│ ├── **init**.py
│ ├── client.py # Binance API client wrapper
│ ├── orders.py # Order execution logic
│ ├── validators.py # Input validation utilities
│ └── logging_config.py # Logging setup
│
├── cli.py # CLI entry point
├── requirements.txt
├── README.md
└── trading_bot.log # Generated log file
```

---

## Requirements

Python 3.8+

Install dependencies:

pip install -r requirements.txt

---

## Setup

1. Clone the repository

```bash
git clone https://github.com/hemantsingh443/trading_bot

cd trading_bot
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a .env file in the project root and add your Binance Testnet API keys

```bash
API_KEY=your_api_key
API_SECRET=your_api_secret
```

API keys can be generated from:

https://testnet.binancefuture.com

---

## Usage

The CLI accepts the following parameters:

symbol Trading pair (example: BTCUSDT)
side Order side (BUY or SELL)
order_type Order type (MARKET or LIMIT)
quantity Order quantity
price Required only for LIMIT orders

---

## Example Commands

Place a MARKET order

```python
python cli.py BTCUSDT BUY MARKET 0.002
```

Place a LIMIT order

```python
python cli.py BTCUSDT BUY LIMIT 0.002 --price 70725.9
```

---

## Example Output

## Order Request Summary

```
Symbol: BTCUSDT
Side: BUY
Type: MARKET
Quantity: 0.002
```

## Order Response

```
Order ID: 12345678
Status: FILLED
Executed Qty: 0.002
Avg Price: 70725.30
```

---

## Logging

All API requests, responses, and errors are logged to:

```
trading_bot.log
```

Example log entry:

```
2026-03-06 11:45:32 | INFO | Placing MARKET order BUY BTCUSDT 0.002
2026-03-06 11:45:33 | INFO | Order response: {...}
```

---

## Validation

The bot performs input validation before sending requests to the API:

- Validates order side (BUY/SELL)
- Validates order type (MARKET/LIMIT)
- Ensures LIMIT orders include a price
- Ensures minimum order value meets Binance requirements

---

## Notes

- This bot interacts only with the Binance Futures Testnet.
- No real funds are used.
- The application is designed for demonstration and evaluation purposes.

---
