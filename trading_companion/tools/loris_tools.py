"""Trading Companion — Loris Tools Integration.

Provides crypto funding rates, arbitrage scanning, and OI data
from https://loris.tools/api — no API key required.
"""

import logging
from typing import Any, Dict, List

import httpx

from tools.registry import registry

logger = logging.getLogger(__name__)

LORIS_API_URL = "https://api.loris.tools/funding"

# Funding intervals by exchange (hours)
_FUNDING_INTERVALS = {
    "hyperliquid": 1,
    "drift": 1,
    "bingx": 1,
    "bitget": 1,
    "phemex": 4,
    "extended": 4,
    "binance": 8,
    "bybit": 8,
    "okx": 8,
    "kucoin": 8,
    "gateio": 8,
    "mexc": 8,
    "cryptocom": 8,
    "htx": 8,
    "lighter": 1,
    "vest": 1,
    "bluefin": 8,
    "paradex": 8,
    "aster": 8,
    "edgex": 8,
    "ethereal": 8,
    "hibachi": 8,
    "pacifica": 8,
    "variational": 8,
    "woofi": 8,
}


def _fetch_loris_data() -> Dict[str, Any]:
    """Fetch funding rates from Loris Tools API."""
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(LORIS_API_URL, headers={"Accept": "application/json"})
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error("Loris API fetch failed: %s", e)
        return {}


def _normalize_rate(value: float, exchange: str) -> float:
    """Normalize funding rate to 8-hour equivalent for fair comparison."""
    interval = _FUNDING_INTERVALS.get(exchange.lower(), 8)
    if interval == 1:
        return value * 8
    if interval == 4:
        return value * 2
    return value


def _format_rate(value: float) -> str:
    """Format funding rate as percentage string."""
    return f"{value:+.4f}%"


def _find_arbitrage_opportunities(data: Dict[str, Any], min_spread: float = 0.01) -> List[Dict[str, Any]]:
    """Find funding rate arbitrage opportunities across exchanges."""
    funding = data.get("funding_rates", {})
    symbols = data.get("symbols", [])
    exchanges = list(funding.keys())

    opportunities = []
    for symbol in symbols:
        rates = {}
        for ex in exchanges:
            raw = funding.get(ex, {}).get(symbol)
            if raw is not None:
                norm = _normalize_rate(raw, ex)
                rates[ex] = {"raw": raw, "norm": norm}

        if len(rates) < 2:
            continue

        max_ex = max(rates, key=lambda x: rates[x]["norm"])
        min_ex = min(rates, key=lambda x: rates[x]["norm"])
        max_rate = rates[max_ex]["norm"]
        min_rate = rates[min_ex]["norm"]
        spread = max_rate - min_rate

        if spread >= min_spread:
            opportunities.append({
                "symbol": symbol,
                "long_exchange": min_ex,  # short funding = get paid to long
                "short_exchange": max_ex,  # high funding = get paid to short
                "long_rate": min_rate,
                "short_rate": max_rate,
                "spread": spread,
                "spread_pct": round(spread * 100, 4),
                "annualized_pct": round(spread * 3 * 365, 2),  # 3x daily (8h intervals)
            })

    opportunities.sort(key=lambda x: x["spread"], reverse=True)
    return opportunities


def _get_extreme_rates(data: Dict[str, Any], top_n: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """Get most positive and most negative funding rates."""
    funding = data.get("funding_rates", {})
    all_rates = []

    for ex, symbols in funding.items():
        for sym, rate in symbols.items():
            if rate is not None:
                norm = _normalize_rate(rate, ex)
                all_rates.append({
                    "symbol": sym,
                    "exchange": ex,
                    "raw_rate": rate,
                    "norm_rate": norm,
                    "norm_pct": round(norm * 100, 4),
                })

    all_rates.sort(key=lambda x: x["norm_rate"], reverse=True)
    return {
        "most_positive": all_rates[:top_n],
        "most_negative": all_rates[-top_n:][::-1],  # reverse to show most negative first
    }


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_fetch_funding_rates(args: dict, **kwargs: Any) -> str:
    """Fetch current funding rates from Loris Tools."""
    data = _fetch_loris_data()
    if not data:
        return "No se pudieron obtener funding rates de Loris Tools."

    symbol = args.get("symbol", "").upper()
    if symbol:
        # Return rates for specific symbol
        funding = data.get("funding_rates", {})
        lines = [f"=== FUNDING RATES — {symbol} ===\n"]
        rates = []
        for ex, symbols in funding.items():
            if symbol in symbols:
                raw = symbols[symbol]
                norm = _normalize_rate(raw, ex)
                rates.append((ex, raw, norm))
        rates.sort(key=lambda x: x[2], reverse=True)
        for ex, raw, norm in rates:
            lines.append(f"  {ex.upper():12} | {raw:+.6f} | (8h eq: {norm:+.6f})")
        return "\n".join(lines)

    # Return summary
    extreme = _get_extreme_rates(data, top_n=5)
    lines = ["=== FUNDING RATES DESTACADOS ===\n"]

    lines.append("🔴 MAYORES FUNDING (pagar para long / cobrar por short):")
    for r in extreme["most_positive"]:
        lines.append(f"  {r['symbol']:8} @ {r['exchange']:12} | {r['norm_pct']:+.4f}%")

    lines.append("\n🟢 MENORES FUNDING (cobrar por long / pagar por short):")
    for r in extreme["most_negative"]:
        lines.append(f"  {r['symbol']:8} @ {r['exchange']:12} | {r['norm_pct']:+.4f}%")

    lines.append(f"\nDatos de {len(data.get('symbols', []))} símbolos en {len(data.get('funding_rates', {}))} exchanges.")
    lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
    return "\n".join(lines)


def _handle_scan_funding_arbitrage(args: dict, **kwargs: Any) -> str:
    """Scan for funding rate arbitrage opportunities."""
    data = _fetch_loris_data()
    if not data:
        return "No se pudieron obtener datos de Loris Tools."

    min_spread = float(args.get("min_spread", 0.01))  # 1% default
    top_n = int(args.get("top_n", 10))
    opportunities = _find_arbitrage_opportunities(data, min_spread=min_spread)

    if not opportunities:
        return f"No se encontraron oportunidades de arbitrage con spread >= {min_spread*100:.2f}%."

    lines = [f"=== ARBITRAGE DE FUNDING — Top {top_n} oportunidades ===\n"]
    lines.append("Estrategia: Long en exchange con funding negativo, Short en exchange con funding positivo\n")

    for opp in opportunities[:top_n]:
        lines.append(
            f"  {opp['symbol']:8} | Spread: {opp['spread_pct']:+.4f}% | "
            f"Anualizado: {opp['annualized_pct']:.1f}%\n"
            f"    → Long  @ {opp['long_exchange']:12} ({opp['long_rate']*100:+.4f}%)\n"
            f"    → Short @ {opp['short_exchange']:12} ({opp['short_rate']*100:+.4f}%)"
        )

    lines.append(f"\nTotal oportunidades encontradas: {len(opportunities)}")
    return "\n".join(lines)


def _handle_funding_cost(args: dict, **kwargs: Any) -> str:
    """Calculate funding cost for a position."""
    symbol = args.get("symbol", "").upper()
    position_size = float(args.get("position_size", 0))
    leverage = float(args.get("leverage", 1))
    hours = int(args.get("hours", 24))

    if not symbol or position_size <= 0:
        return "Se requiere symbol y position_size > 0."

    data = _fetch_loris_data()
    if not data:
        return "No se pudieron obtener funding rates."

    funding = data.get("funding_rates", {})
    lines = [f"=== COSTO DE FUNDING — {symbol} | Pos: ${position_size:,.0f} | Leverage: {leverage}x | {hours}h ===\n"]

    for ex, symbols in funding.items():
        if symbol in symbols:
            raw = symbols[symbol]
            norm = _normalize_rate(raw, ex)
            # Funding is paid on notional (position_size * leverage)
            notional = position_size * leverage
            cost_per_8h = notional * norm
            periods = hours / 8
            total_cost = cost_per_8h * periods
            lines.append(
                f"  {ex.upper():12} | Rate: {norm*100:+.4f}% | "
                f"Costo {hours}h: ${total_cost:+.2f} ({total_cost/position_size*100:+.4f}% del capital)"
            )

    if len(lines) == 1:
        return f"No se encontró {symbol} en los exchanges de Loris Tools."

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_FETCH_FUNDING_RATES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_funding_rates",
        "description": (
            "Obtiene funding rates de cripto perpetuals desde Loris Tools (25+ exchanges). "
            "Muestra los rates más extremos o, si se especifica un símbolo, todos los rates de ese símbolo."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Símbolo opcional, e.g. BTC, ETH, SOL"},
            },
            "required": [],
        },
    },
}

_SCAN_FUNDING_ARBITRAGE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "scan_funding_arbitrage",
        "description": (
            "Escanea oportunidades de arbitrage de funding rates entre exchanges. "
            "Busca diferencias significativas donde se puede hacer long en un exchange (funding negativo = te pagan) "
            "y short en otro (funding positivo = te pagan)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "min_spread": {"type": "number", "default": 0.01, "description": "Spread mínimo (como decimal, e.g. 0.01 = 1%)"},
                "top_n": {"type": "integer", "default": 10, "description": "Número de oportunidades a mostrar"},
            },
            "required": [],
        },
    },
}

_FUNDING_COST_SCHEMA = {
    "type": "function",
    "function": {
        "name": "funding_cost",
        "description": (
            "Calcula el costo de funding para una posición específica en un símbolo dado, "
            "considerando leverage y horizonte temporal."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Símbolo, e.g. BTC, ETH"},
                "position_size": {"type": "number", "description": "Tamaño de la posición en USD"},
                "leverage": {"type": "number", "default": 1, "description": "Apalancamiento, e.g. 5 para 5x"},
                "hours": {"type": "integer", "default": 24, "description": "Horizonte en horas"},
            },
            "required": ["symbol", "position_size"],
        },
    },
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="fetch_funding_rates",
    toolset="loris",
    schema=_FETCH_FUNDING_RATES_SCHEMA,
    handler=_handle_fetch_funding_rates,
    check_fn=lambda: True,
    emoji="💰",
    max_result_size_chars=100_000,
)

registry.register(
    name="scan_funding_arbitrage",
    toolset="loris",
    schema=_SCAN_FUNDING_ARBITRAGE_SCHEMA,
    handler=_handle_scan_funding_arbitrage,
    check_fn=lambda: True,
    emoji="⚖️",
    max_result_size_chars=100_000,
)

registry.register(
    name="funding_cost",
    toolset="loris",
    schema=_FUNDING_COST_SCHEMA,
    handler=_handle_funding_cost,
    check_fn=lambda: True,
    emoji="🧮",
    max_result_size_chars=50_000,
)
