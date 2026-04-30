"""Trading Companion Plugin for Hermes Agent.

Este plugin registra tools de datos de mercado que el agente puede invocar
durante las sesiones de trading.
"""

import logging

logger = logging.getLogger(__name__)


def register(ctx) -> None:
    """Register Trading Companion tools and hooks."""
    logger.info("Loading Trading Companion plugin...")

    # Import tools to trigger auto-registration via registry.register()
    try:
        import trading_companion.tools.market_data
        import trading_companion.tools.wiki_context

        logger.info("Trading Companion tools registered successfully")
    except Exception as e:
        logger.warning("Failed to load Trading Companion tools: %s", e)

    # Register hooks
    ctx.register_hook("on_session_start", _on_session_start)


def _on_session_start(**kwargs) -> None:
    """Log when a session starts."""
    logger.debug("Trading Companion: session started")
