"""
Heartbeat Monitor — polling de signal_events del live engine.

Consultas periodicas a la DB SQLite del live engine, detecta nuevas señales
(entry/exit) desde el último chequeo, y notifica a Reimon.

Uso:
    python -m tools.heartbeat_monitor          # un solo chequeo
    python -m tools.heartbeat_monitor --poll   # loop continuo

Config:
    BACKTESTER_PATH = /home/geminis/backtester
    DB_PATH = {BACKTESTER_PATH}/live_engine/live_engine.db
    STATE_FILE = {DATA_DIR}/heartbeat_state.json
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────────────────
BACKTESTER_PATH = Path(os.environ.get("BACKTESTER_PATH", "/home/geminis/backtester"))
DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "heartbeat_state.json"
# Live engine main.py crea la DB en {BACKTESTER_PATH}/live_engine/live_engine.db
# Si no existe aún, el engine no corrió — no es un error, solo no hay datos.
DB_PATH = BACKTESTER_PATH / "live_engine" / "live_engine.db"
# Fallback: si el engine corrió desde otro dir, buscar el .db real
if not DB_PATH.exists():
    _alt = BACKTESTER_PATH / "algo-live" / "live_engine.db"
    if _alt.exists():
        DB_PATH = _alt

# ── Polling interval default (segundos) ──────────────────────────────────────
DEFAULT_INTERVAL = 300  # 5 min


@dataclass
class SignalEvent:
    id: int
    checked_at: str
    strategy_id: str
    asset: str
    direction: str
    signal_type: str
    price: float
    tp: Optional[float]
    sl: Optional[float]
    emitted_by: str

    def to_display(self) -> str:
        emoji = "🟢" if self.signal_type == "entry" else "🔴"
        tp_str = f" | TP: {self.tp:.2f}" if self.tp else ""
        sl_str = f" | SL: {self.sl:.2f}" if self.sl else ""
        return (
            f"{emoji} *{self.signal_type.upper()}* [{self.strategy_id}]\n"
            f"   {self.asset} {self.direction} @ {self.price:.2f}{tp_str}{sl_str}\n"
            f"   {self.checked_at} · via {self.emitted_by}"
        )


def load_state() -> dict:
    """Carga el último estado del heartbeat (last_id, last_check)."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_id": 0, "last_check": None, "interval": DEFAULT_INTERVAL}


def save_state(state: dict) -> None:
    """Persiste el estado del heartbeat."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def get_new_signals(db_path: Path, last_id: int) -> list[SignalEvent]:
    """Consulta la DB por señales nuevas desde last_id."""
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, checked_at, strategy_id, asset, direction,
                   signal_type, price, tp, sl, emitted_by
            FROM signal_events
            WHERE id > ?
            ORDER BY id ASC
            """,
            (last_id,),
        ).fetchall()
    except sqlite3.OperationalError:
        # Tabla aún no existe — engine no inicializó
        return []
    finally:
        conn.close()

    return [
        SignalEvent(
            id=r["id"],
            checked_at=r["checked_at"],
            strategy_id=r["strategy_id"],
            asset=r["asset"],
            direction=r["direction"],
            signal_type=r["signal_type"],
            price=r["price"],
            tp=r["tp"],
            sl=r["sl"],
            emitted_by=r["emitted_by"],
        )
        for r in rows
    ]


def format_notification(events: list[SignalEvent]) -> str:
    """Formatea lista de eventos para entrega a Reimon."""
    if not events:
        return ""

    header = (
        f"📡 *Heartbeat Signal Report*\n"
        f"`{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}` · "
        f"{len(events)} evento(s)\n"
        f"{'─'*40}"
    )

    body = "\n".join(e.to_display() for e in events)
    return f"{header}\n{body}"


def poll_once(verbose: bool = False) -> list[SignalEvent]:
    """Un solo chequeo. Devuelve eventos nuevos."""
    state = load_state()
    last_id = state.get("last_id", 0)

    events = get_new_signals(DB_PATH, last_id)

    if events:
        state["last_id"] = events[-1].id
        state["last_check"] = datetime.now(timezone.utc).isoformat()
        save_state(state)

    if verbose or events:
        print(f"[heartbeat] last_id={last_id} → new_events={len(events)}")

    return events


def run_loop(interval: Optional[int] = None) -> None:
    """Loop continuo de polling."""
    state = load_state()
    interval = interval or state.get("interval", DEFAULT_INTERVAL)

    print(f"[heartbeat] Starting loop — interval={interval}s — DB={DB_PATH}")

    while True:
        try:
            events = poll_once()
            if events:
                msg = format_notification(events)
                print(msg)
        except Exception as e:
            print(f"[heartbeat] ERROR: {e}", file=sys.stderr)
        time.sleep(interval)


def get_status() -> dict:
    """Estado actual del heartbeat."""
    state = load_state()
    events = get_new_signals(DB_PATH, 0)
    return {
        "state_file": str(STATE_FILE),
        "db_path": str(DB_PATH),
        "db_exists": DB_PATH.exists(),
        "last_id_tracked": state.get("last_id", 0),
        "last_check": state.get("last_check"),
        "interval_seconds": state.get("interval", DEFAULT_INTERVAL),
        "total_events_in_db": len(events),
    }


def set_interval(seconds: int) -> dict:
    """Cambia el intervalo de polling."""
    state = load_state()
    state["interval"] = seconds
    save_state(state)
    return {"interval_seconds": seconds, "saved_to": str(STATE_FILE)}


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Heartbeat Monitor — signal polling")
    parser.add_argument("--poll", action="store_true", help="Loop continuo")
    parser.add_argument("--interval", type=int, default=None, help="Segundos entre polls")
    parser.add_argument("--status", action="store_true", help="Ver estado actual")
    parser.add_argument("--set-interval", type=int, dest="set_interval", help="Cambiar intervalo")
    parser.add_argument("--reset", action="store_true", help="Reset last_id a 0 (re-scan)")
    args = parser.parse_args()

    if args.reset:
        state = load_state()
        state["last_id"] = 0
        save_state(state)
        print(f"[heartbeat] Reset last_id=0")
        return

    if args.status:
        status = get_status()
        print(json.dumps(status, indent=2, default=str))
        return

    if args.set_interval:
        result = set_interval(args.set_interval)
        print(f"[heartbeat] Interval updated: {result}")
        return

    if args.poll:
        run_loop(interval=args.interval)
    else:
        events = poll_once(verbose=True)
        if events:
            print(format_notification(events))
        else:
            print("[heartbeat] No new signals.")


if __name__ == "__main__":
    main()
