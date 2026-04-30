"""Trading Companion — Strategy Monitor Tools for Hermes Agent.

Provides tools to sync, query, and monitor strategies from the backtester project.
"""

import json
import logging
from typing import Any

from tools.registry import registry

from trading_companion.strategies.monitor import StrategyMonitorDB

logger = logging.getLogger(__name__)

monitor = StrategyMonitorDB()

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_sync_strategies(args: dict, **kwargs: Any) -> str:
    """Sync strategies from backtester directories."""
    count = monitor.sync_from_backtester()
    return f"Synced {count} strategies from backtester."


def _handle_list_strategies(args: dict, **kwargs: Any) -> str:
    """List monitored strategies."""
    strategies = monitor.get_strategies(
        status=args.get("status"),
        asset=args.get("asset"),
    )
    if not strategies:
        return "No strategies found."
    lines = [f"Strategies ({len(strategies)}):"]
    for s in strategies:
        emoji = {"live": "🔴", "paper": "🟡", "dry_run": "🔵", "paused": "⚪"}.get(s["status"], "⚪")
        sig_info = ""
        if s["last_signal_type"]:
            sig_info = f" | Last signal: {s['last_signal_type']} @ {s['last_signal_price']} ({s['last_signal_at'][:16]})"
        lines.append(
            f"  {emoji} {s['name']} | {s['asset']} {s['direction']} {s['timeframe']} | Status: {s['status']}{sig_info}"
        )
    return "\n".join(lines)


def _handle_get_strategy_detail(args: dict, **kwargs: Any) -> str:
    """Get detail for a specific strategy."""
    name = args.get("name", "")
    s = monitor.get_strategy(name)
    if not s:
        return f"Strategy '{name}' not found."
    return json.dumps(s, indent=2, default=str, ensure_ascii=False)


def _handle_log_strategy_signal(args: dict, **kwargs: Any) -> str:
    """Log a signal for a monitored strategy."""
    monitor.update_signal(
        name=args["name"],
        signal_type=args["signal_type"],
        price=float(args["price"]),
    )
    return f"Signal logged for {args['name']}: {args['signal_type']} @ {args['price']}"


def _handle_get_active_portfolio(args: dict, **kwargs: Any) -> str:
    """Get all active strategies (dry_run + live + paper)."""
    strategies = monitor.get_active_portfolio()
    if not strategies:
        return "No active strategies."
    lines = [f"Active Portfolio ({len(strategies)} strategies):"]
    for s in strategies:
        lines.append(
            f"  {s['name']} | {s['asset']} {s['direction']} | Status: {s['status']} | Signals today: {s['total_signals_today']}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_SYNC_STRATEGIES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "sync_strategies",
        "description": "Sync strategies from the backtester project into the monitor. Run after adding new strategies.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

_LIST_STRATEGIES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_strategies",
        "description": "List monitored strategies. Can filter by status or asset.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["dry_run", "paper", "live", "paused"]},
                "asset": {"type": "string"},
            },
            "required": [],
        },
    },
}

_GET_STRATEGY_DETAIL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_strategy_detail",
        "description": "Get detailed info for a specific strategy by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Strategy name, e.g. reimon1"},
            },
            "required": ["name"],
        },
    },
}

_LOG_STRATEGY_SIGNAL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "log_strategy_signal",
        "description": "Log a signal (entry/exit) for a monitored strategy. Use when a strategy fires in dry-run or live.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "signal_type": {"type": "string", "enum": ["entry", "exit", "none"]},
                "price": {"type": "number"},
            },
            "required": ["name", "signal_type", "price"],
        },
    },
}

_GET_ACTIVE_PORTFOLIO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_active_portfolio",
        "description": "Get the full active portfolio: all strategies in dry_run, paper, or live status.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="sync_strategies",
    toolset="strategies",
    schema=_SYNC_STRATEGIES_SCHEMA,
    handler=_handle_sync_strategies,
    check_fn=lambda: True,
    emoji="🔄",
    max_result_size_chars=10_000,
)

registry.register(
    name="list_strategies",
    toolset="strategies",
    schema=_LIST_STRATEGIES_SCHEMA,
    handler=_handle_list_strategies,
    check_fn=lambda: True,
    emoji="📋",
    max_result_size_chars=100_000,
)

registry.register(
    name="get_strategy_detail",
    toolset="strategies",
    schema=_GET_STRATEGY_DETAIL_SCHEMA,
    handler=_handle_get_strategy_detail,
    check_fn=lambda: True,
    emoji="🔍",
    max_result_size_chars=50_000,
)

registry.register(
    name="log_strategy_signal",
    toolset="strategies",
    schema=_LOG_STRATEGY_SIGNAL_SCHEMA,
    handler=_handle_log_strategy_signal,
    check_fn=lambda: True,
    emoji="🛎️",
    max_result_size_chars=10_000,
)

registry.register(
    name="get_active_portfolio",
    toolset="strategies",
    schema=_GET_ACTIVE_PORTFOLIO_SCHEMA,
    handler=_handle_get_active_portfolio,
    check_fn=lambda: True,
    emoji="💼",
    max_result_size_chars=100_000,
)
