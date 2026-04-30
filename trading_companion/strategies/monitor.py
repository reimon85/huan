"""Trading Companion — Strategy Monitor.

Integrates with the backtester project to read active strategies,
monitor dry-run signals, and report status to the agent.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Path to the backtester project
BACKTESTER_ROOT = Path("/home/geminis/backtester")
ALGO_LIVE_ROOT = BACKTESTER_ROOT / "algo-live"
STRATEGIES_ROOT = BACKTESTER_ROOT / "strategies"

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "journal.db"


@dataclass
class StrategyEntry:
    """A strategy being monitored."""
    id: Optional[int] = None
    name: str = ""  # e.g. us30_master_sleeve_long_v1
    asset: str = ""
    direction: str = ""  # LONG / SHORT
    timeframe: str = ""
    status: str = ""  # dry_run / paper / live / paused
    regime: str = ""  # e.g. bull, bear, ranging
    source_path: str = ""
    config: str = ""  # JSON string
    last_signal_at: Optional[str] = None
    last_signal_type: Optional[str] = None  # entry / exit / none
    last_signal_price: Optional[float] = None
    total_signals_today: int = 0
    total_trades_week: int = 0
    pnl_week_r: float = 0.0
    notes: str = ""


class StrategyMonitorDB:
    """SQLite persistence for monitored strategies."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    asset TEXT,
                    direction TEXT,
                    timeframe TEXT,
                    status TEXT DEFAULT 'dry_run',
                    regime TEXT,
                    source_path TEXT,
                    config TEXT,
                    last_signal_at TEXT,
                    last_signal_type TEXT,
                    last_signal_price REAL,
                    total_signals_today INTEGER DEFAULT 0,
                    total_trades_week INTEGER DEFAULT 0,
                    pnl_week_r REAL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_strategies_status ON strategies(status);
                CREATE INDEX IF NOT EXISTS idx_strategies_asset ON strategies(asset);
                CREATE INDEX IF NOT EXISTS idx_strategies_regime ON strategies(regime);
                """
            )

    def sync_from_backtester(self) -> int:
        """Scan backtester directories and sync strategies into DB."""
        synced = 0
        # Discover pro strategies
        pro_dir = STRATEGIES_ROOT / "pro"
        if pro_dir.exists():
            for f in pro_dir.glob("*.py"):
                if f.name.startswith("__"):
                    continue
                name = f.stem
                self._upsert_strategy(name, str(f), status="live")
                synced += 1

        # Discover pre strategies
        pre_dir = STRATEGIES_ROOT / "pre"
        if pre_dir.exists():
            for f in pre_dir.glob("*.py"):
                if f.name.startswith("__"):
                    continue
                name = f.stem
                self._upsert_strategy(name, str(f), status="dry_run")
                synced += 1

        # Discover algo-live strategies
        algo_dir = ALGO_LIVE_ROOT / "strategies"
        if algo_dir.exists():
            for sub in algo_dir.rglob("*.py"):
                if sub.name.startswith("__"):
                    continue
                name = sub.stem
                # Determine status from path
                status = "dry_run"
                if "portfolio" in str(sub):
                    status = "dry_run"
                elif "pre" in str(sub):
                    status = "paper"
                self._upsert_strategy(name, str(sub), status=status)
                synced += 1

        return synced

    def _upsert_strategy(self, name: str, source_path: str, status: str) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO strategies (name, source_path, status)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    source_path = excluded.source_path,
                    status = excluded.status
                """,
                (name, source_path, status),
            )
            conn.commit()

    def get_strategies(
        self,
        status: Optional[str] = None,
        asset: Optional[str] = None,
        regime: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM strategies WHERE 1=1"
        params: List[Any] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if asset:
            query += " AND asset = ?"
            params.append(asset)
        if regime:
            query += " AND regime = ?"
            params.append(regime)
        query += " ORDER BY name"
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_strategy(self, name: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM strategies WHERE name = ?", (name,)
            ).fetchone()
            return dict(row) if row else None

    def update_signal(
        self,
        name: str,
        signal_type: str,
        price: float,
        increment_count: bool = True,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE strategies SET
                    last_signal_at = ?,
                    last_signal_type = ?,
                    last_signal_price = ?,
                    total_signals_today = total_signals_today + ?
                WHERE name = ?
                """,
                (datetime.now().isoformat(), signal_type, price, 1 if increment_count else 0, name),
            )
            conn.commit()

    def reset_daily_counts(self) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE strategies SET total_signals_today = 0")
            conn.commit()

    def update_weekly_stats(self, name: str, trades: int, pnl_r: float) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE strategies SET total_trades_week = ?, pnl_week_r = ? WHERE name = ?",
                (trades, pnl_r, name),
            )
            conn.commit()

    def update_status(self, name: str, status: str) -> bool:
        with self._conn() as conn:
            conn.execute(
                "UPDATE strategies SET status = ? WHERE name = ?", (status, name)
            )
            conn.commit()
            return conn.total_changes > 0

    def parse_strategy_file(self, name: str) -> Dict[str, Any]:
        """Parse a strategy .py file to extract metadata."""
        strategy = self.get_strategy(name)
        if not strategy:
            return {}
        path = Path(strategy["source_path"])
        if not path.exists():
            return strategy

        content = path.read_text()
        metadata: Dict[str, Any] = {"name": name, "source_path": str(path)}

        # Extract class name
        for line in content.splitlines():
            if "class " in line and "Strategy" in line:
                metadata["class_name"] = line.split("class ")[1].split("(")[0].strip()
            if "parameters = {" in line or "parameters={" in line:
                # Try to find parameters dict
                pass
            if line.strip().startswith('"') and "=" in line and any(
                x in line for x in ["ema", "z_threshold", "tp_points", "sl_points", "lots"]
            ):
                pass

        return metadata

    def get_active_portfolio(self) -> List[Dict[str, Any]]:
        """Return strategies currently in dry_run or live."""
        return self.get_strategies(status="dry_run") + self.get_strategies(status="live") + self.get_strategies(status="paper")
