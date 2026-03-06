"""
Binance Futures Testnet REST API client wrapper.

Wraps the python-binance UMFutures client (or falls back to direct REST calls)
and provides a single, consistent interface for placing futures orders.

Documentation: https://binance-docs.github.io/apidocs/futures/en/
Testnet base URL: https://testnet.binancefuture.com
"""

import os
import time
import logging
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

from bot.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
FAPI_PATH = "/fapi/v1"


class BinanceFuturesClient:
    """
    Lightweight wrapper around the Binance Futures REST API.
    Uses direct HTTPS requests so there is no dependency on a specific SDK version.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = TESTNET_BASE_URL,
    ) -> None:
        self.api_key = api_key or os.getenv("API_KEY", "")
        self.api_secret = api_secret or os.getenv("API_SECRET", "")
        self.base_url = base_url.rstrip("/")

        if not self.api_key or not self.api_secret:
            raise EnvironmentError(
                "API_KEY and API_SECRET must be set in .env or passed explicitly."
            )

        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        self._time_offset: int = 0  # ms, set by _sync_time()
        self._sync_time()
        logger.info("BinanceFuturesClient initialised (base_url=%s, time_offset=%dms)", self.base_url, self._time_offset)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _sync_time(self) -> None:
        """
        Fetch server time and compute offset vs. local clock.
        Must be called before any signed request to avoid -1021 errors.
        """
        try:
            url = f"{self.base_url}{FAPI_PATH}/time"
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            server_time = resp.json()["serverTime"]  # ms
            local_time = int(time.time() * 1000)
            self._time_offset = server_time - local_time
            logger.debug("Server time sync: offset=%dms", self._time_offset)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not sync server time, offset stays 0: %s", exc)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamp (+server offset) and HMAC-SHA256 signature to a params dict."""
        import hmac
        import hashlib

        params["timestamp"] = int(time.time() * 1000) + self._time_offset
        params["recvWindow"] = 5000  # ms tolerance window
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """
        Send an HTTP request and return the parsed JSON response.
        Raises requests.HTTPError on non-2xx responses.
        """
        params = params or {}
        if signed:
            params = self._sign(params)

        url = f"{self.base_url}{FAPI_PATH}{endpoint}"
        logger.debug("→ %s %s | params=%s", method.upper(), url, params)

        try:
            resp = self._session.request(method, url, params=params, timeout=15)
            logger.debug(
                "← %s %s | status=%s | body=%s",
                method.upper(),
                url,
                resp.status_code,
                resp.text[:500],
            )
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.HTTPError as exc:
            # Surface Binance error codes if available
            try:
                err_body = exc.response.json()
                msg = f"Binance API error {err_body.get('code')}: {err_body.get('msg')}"
            except Exception:
                msg = str(exc)
            logger.error("HTTP error: %s", msg)
            raise requests.HTTPError(msg, response=exc.response) from exc

        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise

        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise

    # ── Public API methods ────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Test connectivity. Returns True if the testnet is reachable."""
        try:
            self._request("GET", "/ping")
            logger.info("Ping successful.")
            return True
        except Exception as exc:
            logger.warning("Ping failed: %s", exc)
            return False

    def get_exchange_info(self) -> Dict[str, Any]:
        """Retrieve exchange information (trading rules, symbol metadata, etc.)."""
        return self._request("GET", "/exchangeInfo")

    def place_order(self, **kwargs) -> Dict[str, Any]:
        """
        Place a new futures order via POST /fapi/v1/order.

        Keyword args map directly to Binance Futures POST /order parameters:
            symbol      : str   (e.g. "BTCUSDT")
            side        : str   ("BUY" | "SELL")
            type        : str   ("MARKET" | "LIMIT")
            quantity    : str   (as string to avoid floating-point issues)
            price       : str   (required for LIMIT)
            timeInForce : str   (default "GTC" for LIMIT orders)
        """
        logger.info("Placing order: %s", kwargs)
        result = self._request("POST", "/order", params=kwargs, signed=True)
        logger.info("Order response: %s", result)
        return result

    def place_algo_order(self, **kwargs) -> Dict[str, Any]:
        """
        Place a Stop-Market or Stop-Limit order via POST /fapi/v1/order/algo.
        Binance Futures routes STOP / STOP_MARKET through the Algo Order endpoint.

        Keyword args include:
            symbol      : str   (e.g. "BTCUSDT")
            side        : str   ("BUY" | "SELL")
            type        : str   ("STOP" | "STOP_MARKET")
            quantity    : str
            stopPrice   : str   (trigger price)
            price       : str   (limit price; required for STOP)
            timeInForce : str   (default "GTC")
        """
        logger.info("Placing algo order: %s", kwargs)
        result = self._request("POST", "/order/algo", params=kwargs, signed=True)
        logger.info("Algo order response: %s", result)
        return result
