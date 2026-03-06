import logging
from .client import get_client
import time 

client = get_client()

def place_market_order(symbol, side, quantity):
    try:
        logging.info(f"Placing MARKET order {side} {symbol} {quantity}")

        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )

        # wait briefly and fetch updated order
        time.sleep(1)

        updated = client.futures_get_order(
            symbol=symbol,
            orderId=order["orderId"]
        )

        logging.info(f"Order response: {updated}")

        return updated

    except Exception as e:
        logging.error(f"Market order failed: {e}")
        raise


def place_limit_order(symbol, side, quantity, price):
    try:
        logging.info(f"Placing LIMIT order {side} {symbol} {quantity} @ {price}")

        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTC"
        )

        logging.info(f"Order response: {order}")

        return order

    except Exception as e:
        logging.error(f"Limit order failed: {e}")
        raise