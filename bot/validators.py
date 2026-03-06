"""
Input validation helpers for the Binance Futures Trading Bot.
All validators raise ValueError with a human-readable message on failure.
"""

from typing import Optional

# Valid values as defined by Binance Futures API
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}   # STOP = stop-limit (bonus)

# STOP and STOP_MARKET require the Binance Algo Order API which is NOT available on
# the Futures Testnet (testnet.binancefuture.com). These types are correct for production.
TESTNET_ALGO_TYPES = {"STOP", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """Normalise and minimally validate a trading pair symbol."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if len(symbol) < 3:
        raise ValueError(f"Symbol '{symbol}' is too short to be valid.")
    # Binance symbols are alphanumeric only
    if not symbol.isalnum():
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use alphanumeric characters only (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Validate order side: BUY or SELL."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Supported types: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    """Validate that quantity is a positive number."""
    if quantity is None:
        raise ValueError("Quantity is required.")
    if not isinstance(quantity, (int, float)):
        raise TypeError(f"Quantity must be a number, got {type(quantity).__name__}.")
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got {quantity}.")
    return float(quantity)


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    Validate price field.
    - LIMIT and STOP orders require a positive price.
    - MARKET / STOP_MARKET orders must NOT supply a price.
    """
    order_type = order_type.upper()
    requires_price = order_type in {"LIMIT", "STOP"}

    if requires_price:
        if price is None:
            raise ValueError(f"Price is required for '{order_type}' orders.")
        if not isinstance(price, (int, float)):
            raise TypeError(f"Price must be a number, got {type(price).__name__}.")
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}.")
        return float(price)
    else:
        # MARKET / STOP_MARKET – price not needed (ignore if supplied)
        return None


def validate_stop_price(stop_price: Optional[float], order_type: str) -> Optional[float]:
    """
    Validate stop_price for STOP (stop-limit) and STOP_MARKET orders.
    """
    order_type = order_type.upper()
    requires_stop = order_type in {"STOP", "STOP_MARKET"}

    if requires_stop:
        if stop_price is None:
            raise ValueError(f"stop_price is required for '{order_type}' orders.")
        if not isinstance(stop_price, (int, float)):
            raise TypeError(f"stop_price must be a number, got {type(stop_price).__name__}.")
        if stop_price <= 0:
            raise ValueError(f"stop_price must be positive, got {stop_price}.")
        return float(stop_price)
    return None


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """Run all validators and return a clean params dict."""
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type),
        "stop_price": validate_stop_price(stop_price, order_type),
    }
