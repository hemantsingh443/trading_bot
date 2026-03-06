import typer
from bot.orders import place_market_order, place_limit_order
from bot.validators import validate_side, validate_order_type, validate_notional
from bot.logging_config import setup_logger

app = typer.Typer()

setup_logger()

@app.command()
def trade(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None
):

    try:
        symbol = symbol.upper()
        side = validate_side(side)
        order_type = validate_order_type(order_type)

        print("\nOrder Request Summary")
        print("----------------------")
        print(f"Symbol: {symbol}")
        print(f"Side: {side}")
        print(f"Type: {order_type}")
        print(f"Quantity: {quantity}")

        if order_type == "LIMIT":

            if price is None:
                raise ValueError("LIMIT order requires price")

            validate_notional(price, quantity)

            print(f"Price: {price}")

            order = place_limit_order(symbol, side, quantity, price)

        elif order_type == "MARKET":

            order = place_market_order(symbol, side, quantity)

        print("\nOrder Response")
        print("----------------------")
        print("Order ID:", order["orderId"])
        print("Status:", order["status"])
        print("Executed Qty:", order["executedQty"])
        print("Avg Price:", order.get("avgPrice"))

    except Exception as e:
        print(f"\n Error: {e}")

if __name__ == "__main__":
    app()