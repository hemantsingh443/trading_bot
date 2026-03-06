def validate_side(side):
    side = side.upper()
    if side not in ["BUY", "SELL"]:
        raise ValueError("Side must be BUY or SELL")
    return side


def validate_order_type(order_type):
    order_type = order_type.upper()
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be MARKET or LIMIT")
    return order_type


def validate_notional(price, quantity, min_notional=100):
    notional = price * quantity
    if notional < min_notional:
        raise ValueError(
            f"Order value ${notional:.2f} is below Binance minimum ${min_notional}"
        )