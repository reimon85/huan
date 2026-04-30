"""Trading Companion — Journal Tools for Hermes Agent.

Provides tools to log trades, query stats, and manage the trading journal.
"""

import json
import logging
from typing import Any

from tools.registry import registry

from trading_companion.journal.db import JournalDB, TradeEntry, SessionEntry

logger = logging.getLogger(__name__)

db = JournalDB()

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_log_trade(args: dict, **kwargs: Any) -> str:
    """Log a single trade to the journal."""
    trade = TradeEntry(
        asset=args.get("asset", ""),
        direction=args.get("direction", ""),
        setup_type=args.get("setup_type", ""),
        entry_price=float(args.get("entry_price", 0)),
        exit_price=float(args["exit_price"]) if args.get("exit_price") else None,
        stop_loss=float(args.get("stop_loss", 0)),
        take_profit=float(args.get("take_profit", 0)),
        result_r=float(args.get("result_r", 0)),
        result_pnl=float(args["result_pnl"]) if args.get("result_pnl") else None,
        planned=args.get("planned", True),
        followed_rules=args.get("followed_rules", True),
        emotions=args.get("emotions", ""),
        notes=args.get("notes", ""),
        tags=args.get("tags", ""),
    )
    trade_id = db.add_trade(trade)
    return f"Trade #{trade_id} logged for {trade.asset} ({trade.direction})."


def _handle_log_session(args: dict, **kwargs: Any) -> str:
    """Log a session debrief to the journal."""
    session = SessionEntry(
        session_date=args.get("session_date"),
        total_result_r=float(args.get("total_result_r", 0)),
        trades_count=int(args.get("trades_count", 0)),
        wins=int(args.get("wins", 0)),
        losses=int(args.get("losses", 0)),
        breakeven=int(args.get("breakeven", 0)),
        lesson=args.get("lesson", ""),
        emotion_state=args.get("emotion_state", ""),
        plan_followed=args.get("plan_followed", True),
        notes=args.get("notes", ""),
    )
    db.add_session(session)
    return f"Session {session.session_date} logged. Result: {session.total_result_r}R."


def _handle_get_stats(args: dict, **kwargs: Any) -> str:
    """Query trading statistics."""
    stats = db.get_stats(
        from_date=args.get("from_date"),
        to_date=args.get("to_date"),
        asset=args.get("asset"),
        setup_type=args.get("setup_type"),
    )
    return json.dumps(stats, indent=2, ensure_ascii=False)


def _handle_get_setup_performance(args: dict, **kwargs: Any) -> str:
    """Get win rate and avg R per setup type."""
    setups = db.get_setup_performance(
        from_date=args.get("from_date"),
        limit=int(args.get("limit", 10)),
    )
    return json.dumps(setups, indent=2, ensure_ascii=False)


def _handle_get_equity_curve(args: dict, **kwargs: Any) -> str:
    """Get weekly cumulative R curve."""
    curve = db.get_weekly_equity_curve(weeks=int(args.get("weeks", 12)))
    return json.dumps(curve, indent=2, ensure_ascii=False)


def _handle_list_recent_trades(args: dict, **kwargs: Any) -> str:
    """List recent trades."""
    trades = db.get_trades(
        from_date=args.get("from_date"),
        asset=args.get("asset"),
        limit=int(args.get("limit", 10)),
    )
    if not trades:
        return "No trades found."
    lines = [f"Recent trades ({len(trades)} shown):"]
    for t in trades:
        lines.append(
            f"  #{t['id']} | {t['session_date']} | {t['asset']} {t['direction']} | "
            f"Setup: {t['setup_type']} | Result: {t['result_r']}R | Planned: {bool(t['planned'])}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_LOG_TRADE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "log_trade",
        "description": "Log a trade to the journal database. Use after a trade is closed.",
        "parameters": {
            "type": "object",
            "properties": {
                "asset": {"type": "string", "description": "e.g. EURUSD, ES, BTC"},
                "direction": {"type": "string", "enum": ["LONG", "SHORT"]},
                "setup_type": {"type": "string", "description": "e.g. order_block, fvg, mean_reversion"},
                "entry_price": {"type": "number"},
                "exit_price": {"type": "number"},
                "stop_loss": {"type": "number"},
                "take_profit": {"type": "number"},
                "result_r": {"type": "number", "description": "Result in R multiples"},
                "result_pnl": {"type": "number", "description": "P&L in currency (optional)"},
                "planned": {"type": "boolean", "description": "Was it in the session plan?"},
                "followed_rules": {"type": "boolean"},
                "emotions": {"type": "string", "description": "Emotional state during trade"},
                "notes": {"type": "string"},
                "tags": {"type": "string", "description": "Comma-separated tags"},
            },
            "required": ["asset", "direction", "result_r"],
        },
    },
}

_LOG_SESSION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "log_session",
        "description": "Log a session debrief summary. Use at end of day.",
        "parameters": {
            "type": "object",
            "properties": {
                "session_date": {"type": "string", "description": "YYYY-MM-DD, defaults to today"},
                "total_result_r": {"type": "number"},
                "trades_count": {"type": "integer"},
                "wins": {"type": "integer"},
                "losses": {"type": "integer"},
                "breakeven": {"type": "integer"},
                "lesson": {"type": "string"},
                "emotion_state": {"type": "string", "enum": ["optimal", "acceptable", "caution"]},
                "plan_followed": {"type": "boolean"},
                "notes": {"type": "string"},
            },
            "required": ["total_result_r", "trades_count"],
        },
    },
}

_GET_STATS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_stats",
        "description": "Get aggregate trading statistics. Can filter by date, asset, or setup.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_date": {"type": "string", "description": "YYYY-MM-DD"},
                "to_date": {"type": "string", "description": "YYYY-MM-DD"},
                "asset": {"type": "string"},
                "setup_type": {"type": "string"},
            },
            "required": [],
        },
    },
}

_GET_SETUP_PERFORMANCE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_setup_performance",
        "description": "Get win rate and average R per setup type. Useful to discover what setups work best.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": [],
        },
    },
}

_GET_EQUITY_CURVE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_equity_curve",
        "description": "Get weekly cumulative R equity curve. Useful for visualizing performance over time.",
        "parameters": {
            "type": "object",
            "properties": {
                "weeks": {"type": "integer", "default": 12},
            },
            "required": [],
        },
    },
}

_LIST_RECENT_TRADES_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_recent_trades",
        "description": "List recent trades from the journal. Useful for review.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_date": {"type": "string", "description": "YYYY-MM-DD"},
                "asset": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": [],
        },
    },
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="log_trade",
    toolset="journal",
    schema=_LOG_TRADE_SCHEMA,
    handler=_handle_log_trade,
    check_fn=lambda: True,
    emoji="📝",
    max_result_size_chars=10_000,
)

registry.register(
    name="log_session",
    toolset="journal",
    schema=_LOG_SESSION_SCHEMA,
    handler=_handle_log_session,
    check_fn=lambda: True,
    emoji="📓",
    max_result_size_chars=10_000,
)

registry.register(
    name="get_stats",
    toolset="journal",
    schema=_GET_STATS_SCHEMA,
    handler=_handle_get_stats,
    check_fn=lambda: True,
    emoji="📊",
    max_result_size_chars=50_000,
)

registry.register(
    name="get_setup_performance",
    toolset="journal",
    schema=_GET_SETUP_PERFORMANCE_SCHEMA,
    handler=_handle_get_setup_performance,
    check_fn=lambda: True,
    emoji="🎯",
    max_result_size_chars=50_000,
)

registry.register(
    name="get_equity_curve",
    toolset="journal",
    schema=_GET_EQUITY_CURVE_SCHEMA,
    handler=_handle_get_equity_curve,
    check_fn=lambda: True,
    emoji="📈",
    max_result_size_chars=50_000,
)

registry.register(
    name="list_recent_trades",
    toolset="journal",
    schema=_LIST_RECENT_TRADES_SCHEMA,
    handler=_handle_list_recent_trades,
    check_fn=lambda: True,
    emoji="📋",
    max_result_size_chars=100_000,
)
