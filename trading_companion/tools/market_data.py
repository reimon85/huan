"""Trading Companion — Market Data Tools (direct sources).

Replaces legacy n8n webhooks with direct market data sources:
- Prices: Yahoo Finance (yfinance)
- Calendar: ForexFactory public JSON feed
- Sentiment: Alternative.me Fear & Greed + Yahoo Finance VIX
- News: ForexLive RSS
- COT: Legacy webhook fallback (CFTC scraping is complex; marked for future)
- Crypto: CoinGecko public API
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any
from xml.etree import ElementTree as ET

import httpx
import yfinance as yf
from bs4 import BeautifulSoup

from tools.registry import registry

logger = logging.getLogger(__name__)

# Legacy webhook fallback (optional)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5678")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _http_get(url: str, timeout: float = 10.0) -> str:
    """Simple HTTP GET returning text or error string."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        return f"[Error: {e}]"


def _http_get_json(url: str, timeout: float = 10.0) -> dict | str:
    """Simple HTTP GET returning parsed JSON or error string."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return f"[Error: {e}]"


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------

_TICKER_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "DXY": "DX-Y.NYB",
    "ES": "ES=F",
    "NQ": "NQ=F",
    "CL": "CL=F",
    "GC": "GC=F",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "VIX": "^VIX",
    "SPX": "^GSPC",
    "NDX": "^IXIC",
}


def _fetch_yf_prices() -> str:
    """Fetch prices via Yahoo Finance."""
    lines = ["=== PRECIOS DE MERCADO ===\n"]
    for name, ticker in _TICKER_MAP.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d", interval="1d")
            if hist.empty:
                continue
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            change = ((last / prev) - 1) * 100 if prev else 0.0
            lines.append(f"{name}: {last:.4f} ({change:+.2f}%)")
        except Exception as e:
            logger.debug("Price fetch failed for %s: %s", name, e)

    if len(lines) == 1:
        return "No se pudieron obtener precios."
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------

def _fetch_calendar() -> str:
    """Fetch economic calendar via ForexFactory public JSON."""
    data = _http_get_json("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
    if isinstance(data, str):
        return f"No se pudo obtener calendario: {data}"

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    events = [e for e in data if e.get("date", "").startswith(today)]

    if not events:
        return f"No hay eventos macro programados para hoy ({today})."

    lines = [f"=== CALENDARIO ECONÓMICO — {today} ===\n"]
    for e in events:
        impact = e.get("impact", "Low")
        if impact in ("High", "Medium"):
            emoji = "🔴" if impact == "High" else "🟡"
            time_str = e.get("date", "")
            if "T" in time_str:
                try:
                    dt = datetime.fromisoformat(time_str)
                    time_str = dt.strftime("%H:%M")
                except Exception:
                    time_str = time_str.split("T")[1][:5]
            lines.append(
                f"{emoji} {time_str} | {e.get('country', '?')} | {e.get('title', '')} "
                f"| Forecast: {e.get('forecast', '-')} | Previous: {e.get('previous', '-')}"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------

def _fetch_sentiment() -> str:
    """Fetch Fear & Greed + VIX."""
    lines = ["=== SENTIMIENTO DE MERCADO ===\n"]

    # Fear & Greed
    fng = _http_get_json("https://api.alternative.me/fng/")
    if isinstance(fng, dict) and fng.get("data"):
        item = fng["data"][0]
        lines.append(
            f"Fear & Greed: {item['value']} — {item.get('value_classification', 'N/A')}"
        )
    else:
        lines.append("Fear & Greed: no disponible")

    # VIX
    try:
        hist = yf.Ticker("^VIX").history(period="2d", interval="1d")
        if not hist.empty:
            last = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else last
            change = ((last / prev) - 1) * 100 if prev else 0.0
            lines.append(f"VIX: {last:.2f} ({change:+.2f}%)")
    except Exception as e:
        logger.debug("VIX fetch failed: %s", e)
        lines.append("VIX: no disponible")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

_NEWS_FEEDS = [
    ("ForexLive", "https://www.forexlive.com/feed/"),
]


def _fetch_news() -> str:
    """Fetch news from RSS feeds."""
    lines = ["=== NOTICIAS RECIENTES ===\n"]
    found = False

    for source_name, url in _NEWS_FEEDS:
        try:
            xml = _http_get(url)
            if xml.startswith("["):
                continue
            root = ET.fromstring(xml.encode("utf-8"))
            items = root.findall(".//item")[:5]
            if items:
                lines.append(f"--- {source_name} ---")
                for item in items:
                    title = item.find("title")
                    if title is not None and title.text:
                        lines.append(f"• {title.text}")
                found = True
        except Exception as e:
            logger.debug("News fetch failed for %s: %s", source_name, e)

    if not found:
        return "No se pudieron obtener noticias."

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# COT (fallback to webhook; direct source is complex)
# ---------------------------------------------------------------------------

def _fetch_cot() -> str:
    """Fetch COT report. Tries legacy webhook first."""
    legacy = _http_get(f"{WEBHOOK_URL}/webhook/cot-latest", timeout=5.0)
    if not legacy.startswith("["):
        return legacy

    # Fallback: informative message
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        f"=== COT REPORT — {today} ===\n"
        "Los datos COT se publican los viernes a las 15:30 ET "
        "con corte al martes anterior.\n"
        "Fuente directa (CFTC.gov) requiere parsing de archivos CSV semanales.\n"
        "Configura el webhook legacy o agrega una fuente directa para COT."
    )


# ---------------------------------------------------------------------------
# Crypto snapshot
# ---------------------------------------------------------------------------

def _fetch_crypto_snapshot() -> str:
    """Fetch crypto snapshot via CoinGecko."""
    data = _http_get_json(
        "https://api.coingecko.com/api/v3/coins/markets?"
        "vs_currency=usd&order=market_cap_desc&per_page=10&page=1&"
        "price_change_percentage=24h"
    )
    if isinstance(data, str):
        return f"No se pudieron obtener datos crypto: {data}"

    lines = ["=== SNAPSHOT CRYPTO ===\n"]
    for coin in data:
        symbol = coin.get("symbol", "").upper()
        price = coin.get("current_price", 0)
        change = coin.get("price_change_percentage_24h", 0) or 0
        mcap = coin.get("market_cap", 0)
        lines.append(
            f"{symbol}: ${price:,.2f} ({change:+.2f}%) | Cap: ${mcap:,.0f}"
        )

    # Add BTC dominance if available
    global_data = _http_get_json("https://api.coingecko.com/api/v3/global")
    if isinstance(global_data, dict):
        dom = global_data.get("data", {}).get("market_cap_percentage", {})
        btc_dom = dom.get("btc", 0)
        eth_dom = dom.get("eth", 0)
        lines.append(f"\nDominance: BTC {btc_dom:.1f}% | ETH {eth_dom:.1f}%")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Market context (aggregates all above)
# ---------------------------------------------------------------------------

def _fetch_market_context(args: dict, **kwargs: Any) -> str:
    """Fetch complete market briefing context from direct sources."""
    parts = [
        _fetch_calendar(),
        _fetch_yf_prices(),
        _fetch_sentiment(),
        _fetch_news(),
        _fetch_crypto_snapshot(),
        _fetch_cot(),
    ]
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Legacy webhook fetchers (kept for backward compat / optional use)
# ---------------------------------------------------------------------------

def _legacy_fetch(endpoint: str) -> str:
    url = f"{WEBHOOK_URL}{endpoint}"
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                return resp.text
            return f"[HTTP {resp.status_code}]"
    except Exception as e:
        return f"[Error: {e}]"


def _handle_fetch_prices(args: dict, **kwargs: Any) -> str:
    return _fetch_yf_prices()


def _handle_fetch_calendar(args: dict, **kwargs: Any) -> str:
    return _fetch_calendar()


def _handle_fetch_sentiment(args: dict, **kwargs: Any) -> str:
    return _fetch_sentiment()


def _handle_fetch_news(args: dict, **kwargs: Any) -> str:
    return _fetch_news()


def _handle_fetch_cot(args: dict, **kwargs: Any) -> str:
    return _fetch_cot()


def _handle_fetch_crypto_snapshot(args: dict, **kwargs: Any) -> str:
    return _fetch_crypto_snapshot()


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------

def _check_internet_available() -> bool:
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get("https://api.coingecko.com/api/v3/ping")
            return resp.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Schemas (unchanged to preserve Hermes registration)
# ---------------------------------------------------------------------------

_FETCH_MARKET_CONTEXT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_market_context",
        "description": (
            "Obtiene el contexto completo de mercado para la sesión actual: "
            "precios, calendario económico, sentiment, noticias, COT y métricas crypto. "
            "Usar al inicio de la conversación o cuando se necesite un panorama general."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_PRICES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_prices",
        "description": "Obtiene precios actuales de los activos monitoreados (Forex, índices, crypto, commodities).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_CALENDAR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_calendar",
        "description": "Obtiene el calendario económico del día con eventos de alto impacto.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_SENTIMENT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_sentiment",
        "description": "Obtiene indicadores de sentimiento del mercado (Fear & Greed, VIX, etc.).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_NEWS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_news",
        "description": "Obtiene noticias recientes y urgentes relevantes para mercados financieros.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_COT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_cot",
        "description": "Obtiene el último reporte COT (Commitment of Traders) del CFTC.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

_FETCH_CRYPTO_SNAPSHOT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_crypto_snapshot",
        "description": (
            "Obtiene snapshot de criptomonedas: funding rates, open interest, "
            "liquidaciones, dominance y market cap."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="fetch_market_context",
    toolset="trading",
    schema=_FETCH_MARKET_CONTEXT_SCHEMA,
    handler=_fetch_market_context,
    check_fn=_check_internet_available,
    emoji="📊",
    max_result_size_chars=200_000,
)

registry.register(
    name="fetch_prices",
    toolset="trading",
    schema=_FETCH_PRICES_SCHEMA,
    handler=_handle_fetch_prices,
    check_fn=_check_internet_available,
    emoji="💹",
    max_result_size_chars=50_000,
)

registry.register(
    name="fetch_calendar",
    toolset="trading",
    schema=_FETCH_CALENDAR_SCHEMA,
    handler=_handle_fetch_calendar,
    check_fn=_check_internet_available,
    emoji="📅",
    max_result_size_chars=50_000,
)

registry.register(
    name="fetch_sentiment",
    toolset="trading",
    schema=_FETCH_SENTIMENT_SCHEMA,
    handler=_handle_fetch_sentiment,
    check_fn=_check_internet_available,
    emoji="🧠",
    max_result_size_chars=50_000,
)

registry.register(
    name="fetch_news",
    toolset="trading",
    schema=_FETCH_NEWS_SCHEMA,
    handler=_handle_fetch_news,
    check_fn=_check_internet_available,
    emoji="📰",
    max_result_size_chars=100_000,
)

registry.register(
    name="fetch_cot",
    toolset="trading",
    schema=_FETCH_COT_SCHEMA,
    handler=_handle_fetch_cot,
    check_fn=_check_internet_available,
    emoji="📈",
    max_result_size_chars=100_000,
)

registry.register(
    name="fetch_crypto_snapshot",
    toolset="trading",
    schema=_FETCH_CRYPTO_SNAPSHOT_SCHEMA,
    handler=_handle_fetch_crypto_snapshot,
    check_fn=_check_internet_available,
    emoji="🪙",
    max_result_size_chars=100_000,
)


# =============================================================================
# Binance Crypto — ccxt (individual price queries)
# =============================================================================

import math
import json as _json


def _format_number(n: float, decimals: int = 4) -> str:
    """Format number with appropriate precision."""
    if n is None or (isinstance(n, float) and math.isnan(n)):
        return "N/A"
    if abs(n) >= 1000:
        return f"{n:,.2f}"
    if abs(n) >= 1:
        return f"{n:.{decimals}f}"
    if abs(n) >= 0.0001:
        return f"{n:.{max(decimals, 6)}f}"
    return f"{n:.8f}"


def _get_binance():
    """Create Binance exchange instance (public, no auth)."""
    import ccxt
    return ccxt.binance()


def _handle_get_crypto_price(args: dict, **kwargs) -> str:
    """Get current price and 24h stats for a crypto asset via Binance."""
    symbol = args.get("symbol", "").strip().upper()
    if not symbol:
        return '{"error": "Symbol is required"}'

    # Normalize: BTC -> BTC/USDT, ETH -> ETH/USDT, etc.
    if "/" not in symbol:
        symbol = f"{symbol}/USDT"

    try:
        exchange = _get_binance()
        ticker = exchange.fetch_ticker(symbol)

        # Funding rate (futures only)
        funding_rate = None
        try:
            funding = exchange.fetch_funding_rate(symbol)
            funding_rate = funding.get("fundingRate")
        except Exception:
            pass

        # Order book spread
        try:
            ob = exchange.fetch_order_book(symbol, limit=1)
            bid = ob.get("bids", [[None]])[0][0]
            ask = ob.get("asks", [[None]])[0][0]
            spread = (ask - bid) / bid * 100 if bid and ask else None
        except Exception:
            bid = ask = spread = None

        result = {
            "exchange": "Binance",
            "symbol": symbol,
            "price": ticker.get("last"),
            "price_formatted": _format_number(ticker.get("last")),
            "bid": bid,
            "ask": ask,
            "spread_pct": round(spread, 4) if spread else None,
            "change_24h": ticker.get("change"),
            "change_pct_24h": ticker.get("percentage"),
            "volume_24h": ticker.get("quoteVolume"),
            "high_24h": ticker.get("high"),
            "low_24h": ticker.get("low"),
            "timestamp": ticker.get("timestamp"),
            "funding_rate": funding_rate,
        }
        return _json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return _json.dumps({"error": str(e), "symbol": symbol})


def _handle_get_crypto_prices(args: dict, **kwargs) -> str:
    """Get prices for multiple crypto assets at once."""
    symbols = args.get("symbols", [])
    if not symbols:
        return '{"error": "No symbols provided"}'

    results = []
    for sym in symbols:
        raw = _handle_get_crypto_price({"symbol": sym}, **kwargs)
        try:
            data = _json.loads(raw)
            if "error" not in data:
                results.append(data)
        except Exception:
            results.append({"symbol": sym, "error": "Parse error"})

    return _json.dumps(results, ensure_ascii=False)


def _check_ccxt_available() -> bool:
    try:
        import ccxt
        return True
    except ImportError:
        return False


_CRYPTO_PRICE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_crypto_price",
        "description": (
            "Get current price and 24h statistics for a cryptocurrency via Binance. "
            "Auto-resolves symbol (BTC -> BTC/USDT). Returns: last price, bid/ask, "
            "spread, 24h change %, volume, high/low, funding rate (futures). "
            "No API key required."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Crypto symbol (e.g. 'BTC', 'ETH', 'SOL'). Case-insensitive.",
                },
            },
            "required": ["symbol"],
        },
    },
}

_CRYPTO_PRICES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_crypto_prices",
        "description": (
            "Get current prices for multiple cryptocurrencies at once via Binance. "
            "More efficient than calling get_crypto_price multiple times."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of crypto symbols (e.g. ['BTC', 'ETH', 'SOL'])",
                },
            },
            "required": ["symbols"],
        },
    },
}


registry.register(
    name="get_crypto_price",
    toolset="trading",
    schema=_CRYPTO_PRICE_SCHEMA,
    handler=_handle_get_crypto_price,
    check_fn=_check_ccxt_available,
    emoji="₿",
)

registry.register(
    name="get_crypto_prices",
    toolset="trading",
    schema=_CRYPTO_PRICES_SCHEMA,
    handler=_handle_get_crypto_prices,
    check_fn=_check_ccxt_available,
    emoji="₿",
)


# =============================================================================
# Hyperliquid Crypto — ccxt (perpetuals)
# =============================================================================

# Hyperliquid perpetual symbols map (base -> ccxt symbol)
_HL_SYMBOLS = {
    "BTC": "BTC/USDC:USDC",
    "ETH": "ETH/USDC:USDC",
    "SOL": "SOL/USDC:USDC",
    "APT": "APT/USDC:USDC",
    "AR": "AR/USDC:USDC",
    "AVAX": "AVAX/USDC:USDC",
    "BNB": "BNB/USDC:USDC",
    "CRV": "CRV/USDC:USDC",
    "DOGE": "DOGE/USDC:USDC",
    "DOT": "DOT/USDC:USDC",
    "FTM": "FTM/USDC:USDC",
    "FXS": "FXS/USDC:USDC",
    "GALA": "GALA/USDC:USDC",
    "LINK": "LINK/USDC:USDC",
    "MATIC": "MATIC/USDC:USDC",
    "OP": "OP/USDC:USDC",
    "ORDI": "ORDI/USDC:USDC",
    "PEPE": "PEPE/USDC:USDC",
    "RDNT": "RDNT/USDC:USDC",
    "RUNE": "RUNE/USDC:USDC",
    "SEI": "SEI/USDC:USDC",
    "SHIB": "SHIB/USDC:USDC",
    "SNX": "SNX/USDC:USDC",
    "SOL": "SOL/USDC:USDC",
    "SUI": "SUI/USDC:USDC",
    "TIA": "TIA/USDC:USDC",
    "TRX": "TRX/USDC:USDC",
    "UNI": "UNI/USDC:USDC",
    "WIF": "WIF/USDC:USDC",
    "XRP": "XRP/USDC:USDC",
}


def _get_hyperliquid():
    """Create Hyperliquid exchange instance (public, no auth)."""
    import ccxt
    return ccxt.hyperliquid()


def _resolve_hl_symbol(symbol: str) -> str:
    """Resolve a symbol to Hyperliquid perpetual format.

    Handles: 'BTC', 'BTC/USDC:USDC', 'BTC/USDT:USDT' -> 'BTC/USDC:USDC'
    """
    symbol = symbol.strip().upper()
    if symbol in _HL_SYMBOLS:
        return _HL_SYMBOLS[symbol]
    # Already full perpetual symbol
    if ":" in symbol:
        return symbol
    # Strip quote and re-map
    base = symbol.replace("/USDT", "").replace("/USDC", "")
    if base in _HL_SYMBOLS:
        return _HL_SYMBOLS[base]
    # Fallback: try constructing
    return f"{base}/USDC:USDC"


def _handle_get_hyperliquid_price(args: dict, **kwargs) -> str:
    """Get current price, funding rate, and order book for a Hyperliquid perpetual."""
    symbol = args.get("symbol", "").strip().upper()
    if not symbol:
        return _json.dumps({"error": "Symbol is required"})

    hl_symbol = _resolve_hl_symbol(symbol)

    try:
        exchange = _get_hyperliquid()
        ticker = exchange.fetch_ticker(hl_symbol)

        # Funding rate
        funding_rate = None
        funding_next = None
        try:
            funding = exchange.fetch_funding_rate(hl_symbol)
            funding_rate = funding.get("fundingRate")
            funding_next = funding.get("nextFundingTime")
        except Exception:
            pass

        # Order book
        bid = ask = spread_pct = None
        try:
            ob = exchange.fetch_order_book(hl_symbol, limit=1)
            bid = ob.get("bids", [[None]])[0][0]
            ask = ob.get("asks", [[None]])[0][0]
            spread_pct = round((ask - bid) / bid * 100, 4) if bid and ask else None
        except Exception:
            pass

        result = {
            "exchange": "Hyperliquid",
            "symbol": hl_symbol,
            "price": ticker.get("last"),
            "price_formatted": _format_number(ticker.get("last")),
            "bid": bid,
            "ask": ask,
            "spread_pct": spread_pct,
            "change_24h": ticker.get("change"),
            "change_pct_24h": ticker.get("percentage"),
            "volume_24h": ticker.get("quoteVolume"),
            "high_24h": ticker.get("high"),
            "low_24h": ticker.get("low"),
            "timestamp": ticker.get("timestamp"),
            "funding_rate": funding_rate,
            "funding_next": funding_next,
        }
        return _json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return _json.dumps({"error": str(e), "symbol": symbol})


def _handle_get_hyperliquid_funding(args: dict, **kwargs) -> str:
    """Get current funding rate for a Hyperliquid perpetual."""
    symbol = args.get("symbol", "").strip().upper()
    if not symbol:
        return _json.dumps({"error": "Symbol is required"})

    hl_symbol = _resolve_hl_symbol(symbol)

    try:
        exchange = _get_hyperliquid()
        funding = exchange.fetch_funding_rate(hl_symbol)

        result = {
            "exchange": "Hyperliquid",
            "symbol": hl_symbol,
            "funding_rate": funding.get("fundingRate"),
            "funding_rate_pct": round(funding.get("fundingRate", 0) * 100, 6),
            "next_funding_time": funding.get("nextFundingTime"),
            "timestamp": funding.get("timestamp"),
        }
        return _json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return _json.dumps({"error": str(e), "symbol": symbol})


def _handle_get_hyperliquid_orderbook(args: dict, **kwargs) -> str:
    """Get order book for a Hyperliquid perpetual."""
    symbol = args.get("symbol", "").strip().upper()
    limit = min(args.get("limit", 10), 50)  # cap at 50

    if not symbol:
        return _json.dumps({"error": "Symbol is required"})

    hl_symbol = _resolve_hl_symbol(symbol)

    try:
        exchange = _get_hyperliquid()
        ob = exchange.fetch_order_book(hl_symbol, limit=limit)

        result = {
            "exchange": "Hyperliquid",
            "symbol": hl_symbol,
            "bids": ob.get("bids", [])[:limit],
            "asks": ob.get("asks", [])[:limit],
            "timestamp": ob.get("timestamp"),
        }
        return _json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return _json.dumps({"error": str(e), "symbol": symbol})


# Schemas

_HYPERLIQUID_PRICE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_hyperliquid_price",
        "description": (
            "Get current price, 24h stats, funding rate, and order book for a "
            "Hyperliquid perpetual. Symbols: BTC, ETH, SOL, etc. "
            "Auto-resolves symbol to Hyperliquid format (e.g. BTC -> BTC/USDC:USDC). "
            "Returns: last price, bid/ask, spread, 24h change %, volume, high/low, "
            "funding rate, next funding time. No API key required."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Perpetual symbol (e.g. 'BTC', 'ETH', 'SOL'). Case-insensitive.",
                },
            },
            "required": ["symbol"],
        },
    },
}

_HYPERLIQUID_FUNDING_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_hyperliquid_funding",
        "description": (
            "Get current funding rate for a Hyperliquid perpetual. "
            "Returns funding rate, rate as percentage, and next funding time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Perpetual symbol (e.g. 'BTC', 'ETH', 'SOL'). Case-insensitive.",
                },
            },
            "required": ["symbol"],
        },
    },
}

_HYPERLIQUID_ORDERBOOK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_hyperliquid_orderbook",
        "description": (
            "Get order book (bids/asks) for a Hyperliquid perpetual. "
            "Returns top N bids and asks (default 10, max 50)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Perpetual symbol (e.g. 'BTC', 'ETH', 'SOL'). Case-insensitive.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of price levels to return (default 10, max 50).",
                    "default": 10,
                },
            },
            "required": ["symbol"],
        },
    },
}


registry.register(
    name="get_hyperliquid_price",
    toolset="trading",
    schema=_HYPERLIQUID_PRICE_SCHEMA,
    handler=_handle_get_hyperliquid_price,
    check_fn=_check_ccxt_available,
    emoji="🔮",
)

registry.register(
    name="get_hyperliquid_funding",
    toolset="trading",
    schema=_HYPERLIQUID_FUNDING_SCHEMA,
    handler=_handle_get_hyperliquid_funding,
    check_fn=_check_ccxt_available,
    emoji="🔮",
)

registry.register(
    name="get_hyperliquid_orderbook",
    toolset="trading",
    schema=_HYPERLIQUID_ORDERBOOK_SCHEMA,
    handler=_handle_get_hyperliquid_orderbook,
    check_fn=_check_ccxt_available,
    emoji="🔮",
)


# =============================================================================
# OANDA — Forex, Indices, Commodities (REST API v20)
# =============================================================================

# OANDA instruments supported by this module
_OANDA_INSTRUMENTS = [
    # Forex Major
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD", "NZD_USD",
    # Forex Minor
    "EUR_GBP", "EUR_JPY", "GBP_JPY", "EUR_CHF", "EUR_AUD", "AUD_JPY",
    "EUR_CAD", "GBP_CHF", "AUD_NZD", "CAD_JPY", "CHF_JPY", "NZD_JPY",
    # Indices
    "US30_USD", "US100_USD", "US500_USD", "DE40_EUR", "GB100_GBP", "FR40_EUR",
    "JP225_USD", "AU200_AUD", "EU50_EUR",
    # Commodities
    "XAU_USD", "XAG_USD", "WTICO_USD", "BCO_USD", "NATGAS_USD",
    "CORN_USD", "WHEAT_USD", "SOYBN_USD",
    # Crypto (via OANDA conversion)
    "BTC_USD", "ETH_USD",
]

# Realistic demo-mode base prices and spreads
_OANDA_DEMO_DATA = {
    # Forex Major (base price, spread in pips)
    "EUR_USD": {"price": 1.08250, "spread_pips": 0.9},
    "GBP_USD": {"price": 1.26500, "spread_pips": 1.2},
    "USD_JPY": {"price": 149.850, "spread_pips": 1.0},
    "USD_CHF": {"price": 0.89200, "spread_pips": 1.3},
    "AUD_USD": {"price": 0.65100, "spread_pips": 1.1},
    "USD_CAD": {"price": 1.35800, "spread_pips": 1.2},
    "NZD_USD": {"price": 0.60300, "spread_pips": 1.3},
    # Forex Minor
    "EUR_GBP": {"price": 0.85600, "spread_pips": 1.5},
    "EUR_JPY": {"price": 162.200, "spread_pips": 1.8},
    "GBP_JPY": {"price": 189.500, "spread_pips": 2.0},
    "EUR_CHF": {"price": 0.96550, "spread_pips": 1.6},
    "EUR_AUD": {"price": 1.66300, "spread_pips": 1.8},
    "AUD_JPY": {"price": 97.500, "spread_pips": 1.5},
    # Indices
    "US30_USD": {"price": 38850.0, "spread_pips": 400},
    "US100_USD": {"price": 17820.0, "spread_pips": 300},
    "US500_USD": {"price": 5248.0, "spread_pips": 150},
    "DE40_EUR": {"price": 18420.0, "spread_pips": 350},
    # Commodities
    "XAU_USD": {"price": 2345.50, "spread_pips": 25},
    "XAG_USD": {"price": 29.850, "spread_pips": 30},
    "WTICO_USD": {"price": 82.15, "spread_pips": 35},
    "NATGAS_USD": {"price": 2.850, "spread_pips": 30},
    "CORN_USD": {"price": 449.50, "spread_pips": 25},
    "WHEAT_USD": {"price": 567.25, "spread_pips": 30},
    # Crypto
    "BTC_USD": {"price": 63500.0, "spread_pips": 1500},
    "ETH_USD": {"price": 3480.0, "spread_pips": 80},
}


def _oanda_is_configured() -> bool:
    """Check if OANDA API credentials are configured via environment."""
    return bool(os.getenv("OANDA_API_KEY") and os.getenv("OANDA_ACCOUNT_ID"))


def _oanda_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _oanda_pricing_url(account_id: str, instruments: list[str]) -> str:
    ids = ",".join(instruments)
    return (
        f"https://api-fxpractice.oanda.com/v3/accounts/{account_id}/pricing"
        f"?instruments={ids}"
    )


def _oanda_instruments_url(account_id: str) -> str:
    return f"https://api-fxpractice.oanda.com/v3/accounts/{account_id}/instruments"


def _fetch_oanda_prices(instruments: list[str]) -> dict | str:
    """Fetch live prices from OANDA API. Returns dict or error string."""
    api_key = os.getenv("OANDA_API_KEY", "")
    account_id = os.getenv("OANDA_ACCOUNT_ID", "")
    url = _oanda_pricing_url(account_id, instruments)
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=_oanda_headers(api_key))
            if resp.status_code == 401:
                return "[Error: OANDA API key inválida o vencida]"
            if resp.status_code == 403:
                return "[Error: OANDA — sin permisos para esta cuenta]"
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        return f"[Error HTTP {e.response.status_code}: {e}]"
    except Exception as e:
        return f"[Error: {e}]"


def _build_demo_price(instrument: str, demo_base: dict) -> dict:
    """Build a realistic mock OANDA pricing response for one instrument."""
    import random
    price = demo_base["price"]
    spread_pips = demo_base["spread_pips"]

    # Add tiny realistic drift
    drift = random.uniform(-0.0003, 0.0003) * price
    price += drift

    # Convert spread pips to price units (1 pip = 0.0001 for forex, 0.01 for JPY, 0.01 for indices, 0.01 for commodities)
    if "_JPY" in instrument or "JPY" in instrument:
        pip = 0.01
    elif "US30" in instrument or "US100" in instrument or "US500" in instrument:
        pip = 1.0
    elif "DE40" in instrument or "GB100" in instrument or "FR40" in instrument or "EU50" in instrument:
        pip = 0.1
    elif "XAU" in instrument:
        pip = 0.01  # gold quoted in cents
    elif "XAG" in instrument:
        pip = 0.005
    elif "WTICO" in instrument or "BCO" in instrument:
        pip = 0.01
    elif "NATGAS" in instrument:
        pip = 0.001
    elif "CORN" in instrument or "WHEAT" in instrument or "SOYBN" in instrument:
        pip = 0.25
    else:
        pip = 0.0001

    half_spread = (spread_pips * pip) / 2
    bid = round(price - half_spread, 5)
    ask = round(price + half_spread, 5)

    return {
        "instrument": instrument,
        "tradeable": True,
        "bids": [{"price": bid, "liquidity": 10_000_000}],
        "asks": [{"price": ask, "liquidity": 10_000_000}],
        "closeoutBid": bid,
        "closeoutAsk": ask,
        "time": f"{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
    }


def _demo_pricing_response(instruments: list[str]) -> dict:
    """Build a mock OANDA /pricing response for demo mode."""
    prices = []
    for inst in instruments:
        inst_norm = inst.replace("_", "_")
        if inst_norm in _OANDA_DEMO_DATA:
            prices.append(_build_demo_price(inst_norm, _OANDA_DEMO_DATA[inst_norm]))
        else:
            # Fallback generic
            prices.append(_build_demo_price(inst_norm, {"price": 1.0, "spread_pips": 2}))
    return {"prices": prices}


# --- OANDA Handlers ---

def _handle_get_oanda_price(args: dict, **kwargs) -> str:
    """Get current price for one or more OANDA instruments (Forex, Indices, Commodities)."""
    instrument = args.get("instrument", "").strip().upper()
    if not instrument:
        return _json.dumps({"error": "instrument es requerido"})

    # Normalize OANDA format (EUR_USD)
    normalized = instrument.replace("/", "_").replace("=", "_")

    if not _oanda_is_configured():
        # Demo mode
        prices = _demo_pricing_response([normalized])["prices"]
        if not prices:
            return _json.dumps({"error": f"Instrumento no soportado en demo: {instrument}"})
        p = prices[0]
        return _json.dumps({
            "source": "OANDA (Demo Mode)",
            "instrument": normalized,
            "price": round((p["bids"][0]["price"] + p["asks"][0]["price"]) / 2, 5),
            "bid": p["bids"][0]["price"],
            "ask": p["asks"][0]["price"],
            "spread_pips": _OANDA_DEMO_DATA.get(normalized, {}).get("spread_pips", "?"),
            "time": p["time"],
        }, ensure_ascii=False)

    data = _fetch_oanda_prices([normalized])
    if isinstance(data, str):
        return _json.dumps({"error": data})

    prices = data.get("prices", [])
    if not prices:
        return _json.dumps({"error": f"No se encontró precio para {instrument}"})

    p = prices[0]
    mid = (p["bids"][0]["price"] + p["asks"][0]["price"]) / 2
    return _json.dumps({
        "source": "OANDA",
        "instrument": p["instrument"],
        "price": mid,
        "bid": p["bids"][0]["price"],
        "ask": p["asks"][0]["price"],
        "spread": round(p["asks"][0]["price"] - p["bids"][0]["price"], 5),
        "time": p["time"],
    }, ensure_ascii=False)


def _handle_get_oanda_prices(args: dict, **kwargs) -> str:
    """Get current prices for multiple OANDA instruments at once."""
    instruments = args.get("instruments", [])
    if not instruments:
        return _json.dumps({"error": "instruments es requerido (lista de instrumentos OANDA)"})

    normalized = [i.strip().replace("/", "_").replace("=", "_") for i in instruments]

    if not _oanda_is_configured():
        prices = _demo_pricing_response(normalized)["prices"]
        result = []
        for p in prices:
            inst = p["instrument"]
            demo = _OANDA_DEMO_DATA.get(inst, {})
            result.append({
                "source": "OANDA (Demo Mode)",
                "instrument": inst,
                "price": round((p["bids"][0]["price"] + p["asks"][0]["price"]) / 2, 5),
                "bid": p["bids"][0]["price"],
                "ask": p["asks"][0]["price"],
                "spread_pips": demo.get("spread_pips", "?"),
                "time": p["time"],
            })
        return _json.dumps(result, ensure_ascii=False)

    data = _fetch_oanda_prices(normalized)
    if isinstance(data, str):
        return _json.dumps({"error": data})

    return _json.dumps(data.get("prices", []), ensure_ascii=False)


def _handle_list_oanda_instruments(args: dict, **kwargs) -> str:
    """List all available OANDA instruments for the account."""
    if not _oanda_is_configured():
        # Return static list in demo mode
        return _json.dumps({
            "source": "OANDA (Demo Mode)",
            "instruments": _OANDA_INSTRUMENTS,
            "count": len(_OANDA_INSTRUMENTS),
        }, ensure_ascii=False)

    account_id = os.getenv("OANDA_ACCOUNT_ID", "")
    api_key = os.getenv("OANDA_API_KEY", "")
    url = _oanda_instruments_url(account_id)
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=_oanda_headers(api_key))
            resp.raise_for_status()
            data = resp.json()
            instruments = [i["name"] for i in data.get("instruments", []) if i.get("tradeable")]
            return _json.dumps({
                "source": "OANDA",
                "instruments": instruments,
                "count": len(instruments),
            }, ensure_ascii=False)
    except Exception as e:
        return _json.dumps({"error": str(e)})


# --- OANDA Schemas ---

_OANDA_PRICE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_oanda_price",
        "description": (
            "Get live price for one OANDA instrument (Forex, Index, Commodity, Crypto). "
            "Supports: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, NZD_USD, "
            "US30_USD, US100_USD, US500_USD, DE40_EUR, XAU_USD, XAG_USD, WTICO_USD, NATGAS_USD, BTC_USD, ETH_USD, etc. "
            "Demo mode (no API key) returns realistic mock data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "instrument": {
                    "type": "string",
                    "description": "OANDA instrument ID (e.g. 'EUR_USD', 'XAU_USD', 'US500_USD'). Case-insensitive.",
                },
            },
            "required": ["instrument"],
        },
    },
}

_OANDA_PRICES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_oanda_prices",
        "description": (
            "Get live prices for multiple OANDA instruments at once. "
            "More efficient than calling get_oanda_price repeatedly. "
            "Demo mode (no API key) returns realistic mock data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "instruments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of OANDA instrument IDs (e.g. ['EUR_USD', 'XAU_USD', 'US500_USD']).",
                },
            },
            "required": ["instruments"],
        },
    },
}

_OANDA_INSTRUMENTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_oanda_instruments",
        "description": (
            "List all tradeable instruments available on the OANDA account. "
            "In demo mode (no API key) returns the full supported instrument list."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def _check_oanda_available() -> bool:
    """OANDA tools are available if API key is set OR if in demo mode (always available)."""
    return True  # Always available; demo mode handles missing credentials


registry.register(
    name="get_oanda_price",
    toolset="trading",
    schema=_OANDA_PRICE_SCHEMA,
    handler=_handle_get_oanda_price,
    check_fn=_check_oanda_available,
    emoji="🌊",
)

registry.register(
    name="get_oanda_prices",
    toolset="trading",
    schema=_OANDA_PRICES_SCHEMA,
    handler=_handle_get_oanda_prices,
    check_fn=_check_oanda_available,
    emoji="🌊",
)

registry.register(
    name="list_oanda_instruments",
    toolset="trading",
    schema=_OANDA_INSTRUMENTS_SCHEMA,
    handler=_handle_list_oanda_instruments,
    check_fn=_check_oanda_available,
    emoji="🌊",
)
