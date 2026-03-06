# Binance Futures Testnet Trading Bot

A Python CLI application that places orders on the Binance Futures Testnet (USDT-M).

## Features

- Place **MARKET**, **LIMIT**, and **Stop-Limit (STOP)** orders
- Supports **BUY** and **SELL** sides
- Clean, layered architecture (client / orders / validators / CLI)
- **Structured logging** to `logs/trading_bot.log` (rotating, 5 MB)
- **Rich** terminal output — styled tables, success/failure panels
- Full input validation with clear error messages
- Exception handling for API errors, network failures, and bad input

## Setup

### 1. Clone and enter the directory

```bash
git clone <repo>
cd Binance-bot
```

### 2. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Create a `.env` file in the project root:

```
API_KEY=your_testnet_api_key
API_SECRET=your_testnet_api_secret
```

> Generate credentials at [Binance Futures Testnet](https://testnet.binancefuture.com)

## How to Run

### 1. Test connectivity

```bash
python cli.py ping
```

### 2. Place a MARKET order

```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 3. Place a LIMIT order

```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
```

### 4. Place a Stop-Limit order (bonus)

```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 90000 --stop-price 91000
```

### 5. Place a Stop-Market order (bonus)

```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 80000
```

### 6. View all options

```bash
python cli.py place-order --help
```

## Project Structure

```
Binance-bot/
├── bot/
│   ├── __init__.py          # Package init — triggers logging setup
│   ├── client.py            # Binance REST API client (direct HTTPS + HMAC-SHA256)
│   ├── orders.py            # Order placement logic (MARKET, LIMIT, Stop-Limit)
│   ├── validators.py        # Input validation helpers
│   └── logging_config.py    # Rotating file + console logging setup
├── cli.py                   # Typer CLI entry point (Rich output)
├── logs/
│   └── trading_bot.log      # Rotating log file (auto-created)
├── .env                     # API credentials (not committed)
├── requirements.txt
└── README.md
```

## Testnet Limitations

> [!NOTE]
> The Binance Futures **Testnet** (`testnet.binancefuture.com`) does NOT support conditional order
> types (`STOP`, `STOP_MARKET`) via the standard REST endpoint — these require the Binance **Algo Order API**
> which is not deployed on the testnet. The implementation in `orders.py` is **production-correct** and will
> work with the production FAPI endpoint (`https://fapi.binance.com`). The CLI displays a clear
> human-friendly message if this limitation is encountered.
>
> **Core MARKET and LIMIT orders work fully on the testnet.**

## Assumptions

- **Testnet only** — `BinanceFuturesClient` defaults to `https://testnet.binancefuture.com`.
- The client auto-syncs its clock with the Binance server time on startup to avoid `-1021` timestamp errors.
- Quantities/prices are sent as strings to Binance to avoid floating-point precision issues.
- `STOP` type maps to Binance's Stop-Limit order (requires both `--price` and `--stop-price`).
- Log level for the file handler is **DEBUG** (full API request/response); console shows **WARNING+** only.
- The `.env` file is expected in the directory from which `cli.py` is invoked.
- Minimum notional value on BTCUSDT testnet is **$100 USD** — use quantity ≥ 0.002 BTC.
