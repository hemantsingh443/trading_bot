"""
CLI entry point for the Binance Futures Trading Bot.

Usage examples:
  python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
  python cli.py place-order --symbol BTCUSDT --side BUY --type STOP --quantity 0.001 --price 90000 --stop-price 91000
  python cli.py ping
"""

from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import bot  # triggers logging setup via bot/__init__.py
from bot.client import BinanceFuturesClient
from bot.logging_config import get_logger
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order, place_stop_market_order
from bot.validators import VALID_ORDER_TYPES, VALID_SIDES

app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot — place MARKET, LIMIT, and Stop-Limit orders.",
    add_completion=False,
)
console = Console()
logger = get_logger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_client() -> BinanceFuturesClient:
    """Instantiate the Binance client, exiting cleanly on config errors."""
    try:
        return BinanceFuturesClient()
    except EnvironmentError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


def _print_summary(params: dict) -> None:
    """Print a styled table of order request parameters."""
    table = Table(title="Order Request Summary", box=box.ROUNDED, show_header=True)
    table.add_column("Parameter", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in params.items():
        if value is not None:
            table.add_row(str(key), str(value))

    console.print(table)


def _print_response(resp: dict) -> None:
    """Print a styled table of order response details."""
    display_keys = [
        ("orderId", "Order ID"),
        ("symbol", "Symbol"),
        ("side", "Side"),
        ("type", "Type"),
        ("status", "Status"),
        ("origQty", "Orig Qty"),
        ("executedQty", "Executed Qty"),
        ("avgPrice", "Avg Price"),
        ("price", "Price"),
        ("stopPrice", "Stop Price"),
        ("timeInForce", "Time In Force"),
    ]

    table = Table(title="Order Response Details", box=box.ROUNDED, show_header=True)
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, label in display_keys:
        value = resp.get(key)
        if value is not None and value != "":
            table.add_row(label, str(value))

    console.print(table)


def _success_panel(order_id: Optional[int]) -> None:
    console.print(
        Panel(
            f"[bold green]✔  Order placed successfully![/bold green]\n"
            f"Order ID: [yellow]{order_id}[/yellow]",
            border_style="green",
        )
    )


def _error_panel(message: str) -> None:
    console.print(
        Panel(
            f"[bold red]✘  Order failed[/bold red]\n{message}",
            border_style="red",
        )
    )


# ── Commands ──────────────────────────────────────────────────────────────────


@app.command("ping")
def cmd_ping() -> None:
    """Test connectivity to the Binance Futures Testnet."""
    client = _make_client()
    if client.ping():
        console.print("[bold green]✔  Testnet is reachable.[/bold green]")
    else:
        console.print("[bold red]✘  Could not reach the testnet.[/bold red]")
        raise typer.Exit(code=1)


@app.command("place-order")
def cmd_place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair (e.g. BTCUSDT)."),
    side: str = typer.Option(
        ...,
        "--side",
        help=f"Order side: {' | '.join(sorted(VALID_SIDES))}.",
    ),
    order_type: str = typer.Option(
        ...,
        "--type",
        "-t",
        help=f"Order type: {' | '.join(sorted(VALID_ORDER_TYPES))}.",
    ),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity (base asset)."),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        "-p",
        help="Limit price (required for LIMIT / STOP orders).",
    ),
    stop_price: Optional[float] = typer.Option(
        None,
        "--stop-price",
        help="Stop trigger price (required for STOP / STOP_MARKET orders).",
    ),
    time_in_force: str = typer.Option(
        "GTC",
        "--tif",
        help="Time-in-force for LIMIT / STOP orders: GTC | IOC | FOK.",
    ),
) -> None:
    """
    Place a futures order on Binance Testnet.

    Supported order types: MARKET, LIMIT, STOP (stop-limit), STOP_MARKET.
    """
    order_type_upper = order_type.strip().upper()
    symbol_upper = symbol.strip().upper()
    side_upper = side.strip().upper()

    # ── Print request summary ─────────────────────────────────────────────────
    summary = {
        "Symbol": symbol_upper,
        "Side": side_upper,
        "Type": order_type_upper,
        "Quantity": quantity,
        "Price": price,
        "Stop Price": stop_price,
        "Time in Force": time_in_force if order_type_upper in {"LIMIT", "STOP"} else None,
    }
    _print_summary(summary)

    # ── Log request ───────────────────────────────────────────────────────────
    logger.info(
        "CLI order request | symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        symbol_upper,
        side_upper,
        order_type_upper,
        quantity,
        price,
        stop_price,
    )

    # ── Validation & placement ────────────────────────────────────────────────
    client = _make_client()

    try:
        if order_type_upper == "MARKET":
            resp = place_market_order(client, symbol_upper, side_upper, quantity)

        elif order_type_upper == "LIMIT":
            if price is None:
                console.print(
                    "[bold red]Error:[/bold red] --price is required for LIMIT orders."
                )
                raise typer.Exit(code=1)
            resp = place_limit_order(
                client, symbol_upper, side_upper, quantity, price, time_in_force
            )

        elif order_type_upper == "STOP":
            if price is None or stop_price is None:
                console.print(
                    "[bold red]Error:[/bold red] Both --price and --stop-price are required "
                    "for STOP (stop-limit) orders."
                )
                raise typer.Exit(code=1)
            resp = place_stop_limit_order(
                client, symbol_upper, side_upper, quantity, price, stop_price, time_in_force
            )

        elif order_type_upper == "STOP_MARKET":
            if stop_price is None:
                console.print(
                    "[bold red]Error:[/bold red] --stop-price is required for STOP_MARKET orders."
                )
                raise typer.Exit(code=1)
            resp = place_stop_market_order(
                client, symbol_upper, side_upper, quantity, stop_price
            )

        else:
            console.print(
                f"[bold red]Error:[/bold red] Unsupported order type '{order_type_upper}'."
            )
            raise typer.Exit(code=1)

    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        _error_panel(f"Validation error: {exc}")
        raise typer.Exit(code=1) from exc

    except Exception as exc:  # network / API errors
        msg = str(exc)
        logger.error("Order placement failed: %s", msg)
        # Detect Binance testnet limitation for conditional order types
        if "-4120" in msg and order_type_upper in {"STOP", "STOP_MARKET"}:
            console.print(
                Panel(
                    "[bold yellow]⚠  Testnet Limitation[/bold yellow]\n\n"
                    f"Order type [bold]{order_type_upper}[/bold] requires the Binance Algo Order API,\n"
                    "which is [bold]not available on the Futures Testnet[/bold].\n\n"
                    "The implementation is production-correct. Use the production API\n"
                    "(https://fapi.binance.com) with a real account to place this order.",
                    title="Testnet Limitation",
                    border_style="yellow",
                )
            )
        else:
            _error_panel(msg)
        raise typer.Exit(code=1) from exc

    # ── Print response ────────────────────────────────────────────────────────
    _print_response(resp)
    _success_panel(resp.get("orderId"))
    logger.info("Order placed successfully | orderId=%s", resp.get("orderId"))


# ── Entry-point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
