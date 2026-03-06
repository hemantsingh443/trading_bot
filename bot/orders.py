"""
Order placement logic for the Binance Futures Trading Bot.

All public functions return a normalised response dict with keys:
    orderId, symbol, side, type, status, executedQty, avgPrice, origQty, price
"""

from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient
from bot.logging_config import get_logger
from bot.validators import validate_all

logger = get_logger(__name__)


def _normalise_response(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the most relevant fields from the raw Binance response."""
    return {
        "orderId": raw.get("orderId"),
        "symbol": raw.get("symbol"),
        "side": raw.get("side"),
        "type": raw.get("type"),
        "status": raw.get("status"),
        "origQty": raw.get("origQty"),
        "executedQty": raw.get("executedQty"),
        "avgPrice": raw.get("avgPrice"),
        "price": raw.get("price"),
        "stopPrice": raw.get("stopPrice"),
        "timeInForce": raw.get("timeInForce"),
        "updateTime": raw.get("updateTime"),
        # Include full raw response for logging
        "_raw": raw,
    }


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Dict[str, Any]:
    """
    Place a MARKET order.

    Args:
        client   : Authenticated BinanceFuturesClient
        symbol   : Trading pair, e.g. "BTCUSDT"
        side     : "BUY" or "SELL"
        quantity : Order size in base asset

    Returns:
        Normalised order response dict
    """
    params = validate_all(symbol=symbol, side=side, order_type="MARKET", quantity=quantity)

    api_params = {
        "symbol": params["symbol"],
        "side": params["side"],
        "type": "MARKET",
        "quantity": f"{params['quantity']:g}",
    }

    logger.info(
        "Placing MARKET order | symbol=%s side=%s qty=%s",
        params["symbol"],
        params["side"],
        api_params["quantity"],
    )

    raw = client.place_order(**api_params)
    return _normalise_response(raw)


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """
    Place a LIMIT order.

    Args:
        client        : Authenticated BinanceFuturesClient
        symbol        : Trading pair, e.g. "BTCUSDT"
        side          : "BUY" or "SELL"
        quantity      : Order size in base asset
        price         : Limit price
        time_in_force : "GTC" (default), "IOC", or "FOK"

    Returns:
        Normalised order response dict
    """
    params = validate_all(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
    )

    api_params = {
        "symbol": params["symbol"],
        "side": params["side"],
        "type": "LIMIT",
        "quantity": f"{params['quantity']:g}",
        "price": f"{params['price']:g}",
        "timeInForce": time_in_force,
    }

    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
        params["symbol"],
        params["side"],
        api_params["quantity"],
        api_params["price"],
        time_in_force,
    )

    raw = client.place_order(**api_params)
    return _normalise_response(raw)


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """
    Place a STOP (Stop-Limit) order via the Algo Order API — bonus order type.

    The order becomes a LIMIT order once the stop_price is triggered.

    Args:
        client      : Authenticated BinanceFuturesClient
        symbol      : Trading pair, e.g. "BTCUSDT"
        side        : "BUY" or "SELL"
        quantity    : Order size in base asset
        price       : Limit price (executed after stop is hit)
        stop_price  : Trigger price
        time_in_force: "GTC" (default), "IOC", or "FOK"

    Returns:
        Normalised order response dict
    """
    params = validate_all(
        symbol=symbol,
        side=side,
        order_type="STOP",
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    api_params = {
        "symbol": params["symbol"],
        "side": params["side"],
        "type": "STOP",
        "quantity": f"{params['quantity']:g}",
        "price": f"{params['price']:g}",
        "stopPrice": f"{params['stop_price']:g}",
        "timeInForce": time_in_force,
    }

    logger.info(
        "Placing STOP-LIMIT order | symbol=%s side=%s qty=%s price=%s stopPrice=%s",
        params["symbol"],
        params["side"],
        api_params["quantity"],
        api_params["price"],
        api_params["stopPrice"],
    )

    raw = client.place_algo_order(**api_params)
    return _normalise_response(raw)


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> Dict[str, Any]:
    """
    Place a STOP_MARKET order via the Algo Order API — bonus order type.

    Triggers a market order when stop_price is reached.

    Args:
        client     : Authenticated BinanceFuturesClient
        symbol     : Trading pair, e.g. "BTCUSDT"
        side       : "BUY" or "SELL"
        quantity   : Order size in base asset
        stop_price : Trigger price

    Returns:
        Normalised order response dict
    """
    params = validate_all(
        symbol=symbol,
        side=side,
        order_type="STOP_MARKET",
        quantity=quantity,
        stop_price=stop_price,
    )

    api_params = {
        "symbol": params["symbol"],
        "side": params["side"],
        "type": "STOP_MARKET",
        "quantity": f"{params['quantity']:g}",
        "stopPrice": f"{params['stop_price']:g}",
    }

    logger.info(
        "Placing STOP-MARKET order | symbol=%s side=%s qty=%s stopPrice=%s",
        params["symbol"],
        params["side"],
        api_params["quantity"],
        api_params["stopPrice"],
    )

    raw = client.place_algo_order(**api_params)
    return _normalise_response(raw)
