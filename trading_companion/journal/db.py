"""Trading Journal — SQLite persistence for trades, emotions, and metrics.

This module provides a structured journal where the agent can log trades,
debrief sessions, and compute statistics. It replaces ad-hoc MEMORY.md
updates with queryable data.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "journal.db"


@dataclass
class TradeEntry:
    """A single trade log."""
    id: Optional[int] = None
    timestamp: Optional[str] = None
    session_date: Optional[str] = None
    asset: str = ""
    direction: str = ""  # LONG / SHORT
    setup_type: str = ""  # e.g. order_block, fvg, mean_reversion
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    stop_loss: float = 0.0
    take_profit: float = 0.0
    result_r: float = 0.0
    result_pnl: Optional[float] = None
    planned: bool = True  # Was it in the session plan?
    followed_rules: bool = True
    emotions: str = ""  # JSON string or free text
    notes: str = ""
    tags: str = ""  # comma-separated
    screenshot_path: Optional[str] = None


@dataclass
class SessionEntry:
    """A trading session debrief."""
    id: Optional[int] = None
    session_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    markets: str = ""  # comma-separated
    total_result_r: float = 0.0
    trades_count: int = 0
    wins: int = 0
    losses: int = 0
    breakeven: int = 0
    lesson: str = ""
    emotion_state: str = ""  # optimal / acceptable / caution
    sleep_quality: Optional[str] = None
    stress_level: Optional[str] = None
    plan_followed: bool = True
    notes: str = ""


class JournalDB:
    """SQLite journal with trades and sessions tables."""

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
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    session_date TEXT,
                    asset TEXT NOT NULL,
                    direction TEXT CHECK(direction IN ('LONG','SHORT','')),
                    setup_type TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    result_r REAL DEFAULT 0,
                    result_pnl REAL,
                    planned INTEGER DEFAULT 1,
                    followed_rules INTEGER DEFAULT 1,
                    emotions TEXT,
                    notes TEXT,
                    tags TEXT,
                    screenshot_path TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(session_date);
                CREATE INDEX IF NOT EXISTS idx_trades_asset ON trades(asset);
                CREATE INDEX IF NOT EXISTS idx_trades_setup ON trades(setup_type);

                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_date TEXT UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    markets TEXT,
                    total_result_r REAL DEFAULT 0,
                    trades_count INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    breakeven INTEGER DEFAULT 0,
                    lesson TEXT,
                    emotion_state TEXT,
                    sleep_quality TEXT,
                    stress_level TEXT,
                    plan_followed INTEGER DEFAULT 1,
                    notes TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);
                """
            )

    # ------------------------------------------------------------------
    # Trades
    # ------------------------------------------------------------------

    def add_trade(self, trade: TradeEntry) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO trades
                (session_date, asset, direction, setup_type, entry_price, exit_price,
                 stop_loss, take_profit, result_r, result_pnl, planned, followed_rules,
                 emotions, notes, tags, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade.session_date or date.today().isoformat(),
                    trade.asset,
                    trade.direction,
                    trade.setup_type,
                    trade.entry_price,
                    trade.exit_price,
                    trade.stop_loss,
                    trade.take_profit,
                    trade.result_r,
                    trade.result_pnl,
                    int(trade.planned),
                    int(trade.followed_rules),
                    trade.emotions,
                    trade.notes,
                    trade.tags,
                    trade.screenshot_path,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_trades(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        asset: Optional[str] = None,
        setup_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM trades WHERE 1=1"
        params: List[Any] = []
        if from_date:
            query += " AND session_date >= ?"
            params.append(from_date)
        if to_date:
            query += " AND session_date <= ?"
            params.append(to_date)
        if asset:
            query += " AND asset = ?"
            params.append(asset)
        if setup_type:
            query += " AND setup_type = ?"
            params.append(setup_type)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def update_trade_exit(self, trade_id: int, exit_price: float, result_r: float, result_pnl: Optional[float] = None) -> bool:
        with self._conn() as conn:
            conn.execute(
                "UPDATE trades SET exit_price = ?, result_r = ?, result_pnl = ? WHERE id = ?",
                (exit_price, result_r, result_pnl, trade_id),
            )
            conn.commit()
            return conn.total_changes > 0

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def add_session(self, session: SessionEntry) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO sessions
                (session_date, start_time, end_time, markets, total_result_r,
                 trades_count, wins, losses, breakeven, lesson, emotion_state,
                 sleep_quality, stress_level, plan_followed, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_date or date.today().isoformat(),
                    session.start_time,
                    session.end_time,
                    session.markets,
                    session.total_result_r,
                    session.trades_count,
                    session.wins,
                    session.losses,
                    session.breakeven,
                    session.lesson,
                    session.emotion_state,
                    session.sleep_quality,
                    session.stress_level,
                    int(session.plan_followed),
                    session.notes,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_session(self, session_date: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_date = ?", (session_date,)
            ).fetchone()
            return dict(row) if row else None

    def get_sessions(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY session_date DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Metrics / Stats
    # ------------------------------------------------------------------

    def get_stats(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        asset: Optional[str] = None,
        setup_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compute aggregate statistics for the filtered trades."""
        where = []
        params: List[Any] = []
        if from_date:
            where.append("session_date >= ?")
            params.append(from_date)
        if to_date:
            where.append("session_date <= ?")
            params.append(to_date)
        if asset:
            where.append("asset = ?")
            params.append(asset)
        if setup_type:
            where.append("setup_type = ?")
            params.append(setup_type)
        clause = " AND ".join(where) if where else "1=1"

        with self._conn() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            wins = conn.execute(
                f"SELECT COUNT(*) FROM trades WHERE {clause} AND result_r > 0", params
            ).fetchone()[0]

            losses = conn.execute(
                f"SELECT COUNT(*) FROM trades WHERE {clause} AND result_r < 0", params
            ).fetchone()[0]

            breakeven = conn.execute(
                f"SELECT COUNT(*) FROM trades WHERE {clause} AND result_r = 0", params
            ).fetchone()[0]

            sum_r = conn.execute(
                f"SELECT COALESCE(SUM(result_r), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            avg_r = conn.execute(
                f"SELECT COALESCE(AVG(result_r), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            avg_win = conn.execute(
                f"SELECT COALESCE(AVG(result_r), 0) FROM trades WHERE {clause} AND result_r > 0", params
            ).fetchone()[0]

            avg_loss = conn.execute(
                f"SELECT COALESCE(AVG(result_r), 0) FROM trades WHERE {clause} AND result_r < 0", params
            ).fetchone()[0]

            max_r = conn.execute(
                f"SELECT COALESCE(MAX(result_r), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            min_r = conn.execute(
                f"SELECT COALESCE(MIN(result_r), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            planned = conn.execute(
                f"SELECT COALESCE(SUM(planned), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

            followed = conn.execute(
                f"SELECT COALESCE(SUM(followed_rules), 0) FROM trades WHERE {clause}", params
            ).fetchone()[0]

        win_rate = (wins / total * 100) if total > 0 else 0
        profit_factor = abs((avg_win * wins) / (avg_loss * losses)) if (losses and avg_loss) else float('inf') if wins else 0
        expectancy = avg_r
        planned_pct = (planned / total * 100) if total else 0
        followed_pct = (followed / total * 100) if total else 0

        return {
            "period": f"{from_date or 'all'} to {to_date or 'today'}",
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "breakeven": breakeven,
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "inf",
            "total_r": round(sum_r, 2),
            "avg_r": round(avg_r, 2),
            "avg_win_r": round(avg_win, 2),
            "avg_loss_r": round(avg_loss, 2),
            "max_r": round(max_r, 2),
            "min_r": round(min_r, 2),
            "expectancy": round(expectancy, 2),
            "planned_pct": round(planned_pct, 2),
            "followed_rules_pct": round(followed_pct, 2),
        }

    def get_setup_performance(self, from_date: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Win rate and avg R per setup type."""
        where = "WHERE session_date >= ?" if from_date else ""
        params = [from_date] if from_date else []
        with self._conn() as conn:
            rows = conn.execute(
                f"""
                SELECT setup_type,
                       COUNT(*) as total,
                       SUM(CASE WHEN result_r > 0 THEN 1 ELSE 0 END) as wins,
                       AVG(result_r) as avg_r,
                       SUM(result_r) as total_r
                FROM trades
                {where}
                AND setup_type != ''
                GROUP BY setup_type
                ORDER BY total DESC
                LIMIT ?
                """,
                params + [limit],
            ).fetchall()
            return [
                {
                    "setup": row["setup_type"],
                    "total": row["total"],
                    "wins": row["wins"],
                    "win_rate_pct": round(row["wins"] / row["total"] * 100, 1) if row["total"] else 0,
                    "avg_r": round(row["avg_r"] or 0, 2),
                    "total_r": round(row["total_r"] or 0, 2),
                }
                for row in rows
            ]

    def get_weekly_equity_curve(self, weeks: int = 12) -> List[Dict[str, Any]]:
        """Weekly cumulative R for equity curve."""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT strftime('%Y-%W', session_date) as week,
                       SUM(result_r) as weekly_r
                FROM trades
                WHERE session_date >= date('now', '-{} weeks')
                GROUP BY week
                ORDER BY week
                """.format(weeks)
            ).fetchall()
            curve = []
            cumulative = 0.0
            for row in rows:
                cumulative += row["weekly_r"]
                curve.append({
                    "week": row["week"],
                    "weekly_r": round(row["weekly_r"], 2),
                    "cumulative_r": round(cumulative, 2),
                })
            return curve
