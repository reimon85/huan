"""Trading Companion — Screener Tool for Hermes Agent.

Provides market scanning capabilities to find trading opportunities.
"""

import logging
from typing import Any

from tools.registry import registry

from trading_companion.screener.core import scan_universe, format_scan

logger = logging.getLogger(__name__)


def _handle_scan_market(args: dict, **kwargs: Any) -> str:
    """Scan the market for opportunities."""
    results = scan_universe()
    top_n = int(args.get("top_n", 10))
    return format_scan(results, top_n=top_n)


_SCAN_MARKET_SCHEMA = {
    "type": "function",
    "function": {
        "name": "scan_market",
        "description": (
            "Escanea el mercado buscando oportunidades de trading. "
            "Detecta: cruces de EMA, compresión de rango, gaps, spikes de volumen, "
            "proximidad a soportes/resistencias. Devuelve resultados priorizados por score."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "default": 10, "description": "Número de resultados a mostrar"},
            },
            "required": [],
        },
    },
}

registry.register(
    name="scan_market",
    toolset="screener",
    schema=_SCAN_MARKET_SCHEMA,
    handler=_handle_scan_market,
    check_fn=lambda: True,
    emoji="🔭",
    max_result_size_chars=100_000,
)
