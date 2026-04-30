"""Trading Companion — Heartbeat Monitor Tools for Hermes Agent.

Polls signal_events from the live engine SQLite DB and detects new signals.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

# Add trading_companion to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.registry import registry
from tools.heartbeat_monitor import (
    poll_once,
    get_status,
    load_state,
    save_state,
    format_notification,
    SignalEvent,
    STATE_FILE,
    DB_PATH,
    DEFAULT_INTERVAL,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_check_signals(args: dict, **kwargs: Any) -> str:
    """Poll for new signals since last check. Returns notification text."""
    events = poll_once()
    if not events:
        return "No new signals since last check."
    return format_notification(events)


def _handle_heartbeat_status(args: dict, **kwargs: Any) -> str:
    """Show heartbeat monitoring status."""
    status = get_status()
    lines = [
        f"DB Path: {status['db_path']}",
        f"DB exists: {status['db_exists']}",
        f"Last ID tracked: {status['last_id_tracked']}",
        f"Last check: {status['last_check'] or 'never'}",
        f"Interval: {status['interval_seconds']}s ({status['interval_seconds']//60}min)",
        f"State file: {status['state_file']}",
    ]
    return "\n".join(lines)


def _handle_set_heartbeat_interval(args: dict, **kwargs: Any) -> str:
    """Set the heartbeat polling interval in seconds."""
    seconds = args.get("seconds", 300)
    if seconds < 30:
        return "Interval must be at least 30 seconds."
    result = {"interval_seconds": seconds}
    state = load_state()
    state["interval"] = seconds
    save_state(state)
    return f"Heartbeat interval set to {seconds}s ({seconds//60}min). Saved to {STATE_FILE}."


def _handle_reset_heartbeat(args: dict, **kwargs: Any) -> str:
    """Reset heartbeat last_id to 0 (re-scan all events)."""
    state = load_state()
    state["last_id"] = 0
    save_state(state)
    return "Heartbeat reset: last_id=0. Next check will rescan all events."


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

_CHECK_SIGNALS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_signals",
        "description": "Poll the live engine DB for new entry/exit signals since last check. Returns formatted notification if there are new signals.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

_HEARTBEAT_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "heartbeat_status",
        "description": "Show heartbeat monitor status: DB path, last ID tracked, interval, state file.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

_SET_HEARTBEAT_INTERVAL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "set_heartbeat_interval",
        "description": "Set the heartbeat polling interval in seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {"type": "integer", "description": "Interval in seconds (min: 30)."},
            },
            "required": ["seconds"],
        },
    },
}

_RESET_HEARTBEAT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reset_heartbeat",
        "description": "Reset heartbeat last_id to 0. Next check will rescan ALL events in the DB from the beginning. Use when you want to re-process existing signals.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="check_signals",
    toolset="strategies",
    schema=_CHECK_SIGNALS_SCHEMA,
    handler=_handle_check_signals,
    check_fn=lambda: True,
    emoji="📡",
    max_result_size_chars=10_000,
)

registry.register(
    name="heartbeat_status",
    toolset="strategies",
    schema=_HEARTBEAT_STATUS_SCHEMA,
    handler=_handle_heartbeat_status,
    check_fn=lambda: True,
    emoji="💓",
    max_result_size_chars=5_000,
)

registry.register(
    name="set_heartbeat_interval",
    toolset="strategies",
    schema=_SET_HEARTBEAT_INTERVAL_SCHEMA,
    handler=_handle_set_heartbeat_interval,
    check_fn=lambda: True,
    emoji="⏱️",
    max_result_size_chars=2_000,
)

registry.register(
    name="reset_heartbeat",
    toolset="strategies",
    schema=_RESET_HEARTBEAT_SCHEMA,
    handler=_handle_reset_heartbeat,
    check_fn=lambda: True,
    emoji="🔁",
    max_result_size_chars=2_000,
)
