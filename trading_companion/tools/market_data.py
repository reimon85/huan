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
