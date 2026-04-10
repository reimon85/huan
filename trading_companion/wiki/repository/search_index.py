"""SQLite FTS5 search index implementation."""

import sqlite3
from pathlib import Path
from typing import Optional
from uuid import UUID

from trading_companion.core.config import Settings, get_settings
from trading_companion.core.exceptions import SearchError
from trading_companion.wiki.models import WikiNode


class SearchIndex:
    """
    SQLite FTS5 full-text search index for wiki nodes.

    Provides fast full-text search across node titles, content, and tags.
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.db_path = self.settings.wiki_db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self) -> None:
        """Ensure database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize the FTS5 virtual table if it doesn't exist."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
                    id,
                    title,
                    branch,
                    content,
                    summary,
                    tags,
                    tokenize='porter unicode61'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wiki_fts_meta (
                    id TEXT PRIMARY KEY,
                    node_id TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def index_node(self, node: WikiNode) -> None:
        """Add or update a node in the search index."""
        conn = self._get_connection()
        try:
            # Delete existing entry
            conn.execute("DELETE FROM wiki_fts WHERE id = ?", (str(node.id),))
            conn.execute(
                "DELETE FROM wiki_fts_meta WHERE id = ?", (str(node.id),)
            )

            # Insert new entry
            conn.execute(
                """
                INSERT INTO wiki_fts (id, title, branch, content, summary, tags)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(node.id),
                    node.title,
                    node.branch or "",
                    node.content,
                    node.summary,
                    " ".join(node.tags) if node.tags else "",
                ),
            )

            # Update metadata
            conn.execute(
                """
                INSERT INTO wiki_fts_meta (id, node_id, updated_at)
                VALUES (?, ?, ?)
                """,
                (str(node.id), str(node.id), node.updated_at.isoformat()),
            )

            conn.commit()
        except sqlite3.Error as e:
            raise SearchError(f"Failed to index node: {e}")
        finally:
            conn.close()

    def remove_node(self, node_id: UUID) -> None:
        """Remove a node from the search index."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM wiki_fts WHERE id = ?", (str(node_id),))
            conn.execute("DELETE FROM wiki_fts_meta WHERE id = ?", (str(node_id),))
            conn.commit()
        except sqlite3.Error as e:
            raise SearchError(f"Failed to remove node from index: {e}")
        finally:
            conn.close()

    def search(
        self,
        query: str,
        branch: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Perform full-text search on wiki nodes.

        Args:
            query: Search query string
            branch: Optional branch to filter by
            limit: Maximum results to return
            offset: Offset for pagination

        Returns:
            List of matching documents with relevance scores
        """
        conn = self._get_connection()
        try:
            # Build FTS5 query (handle basic operators)
            fts_query = self._build_fts_query(query)

            if branch:
                sql = """
                    SELECT id, title, branch, summary,
                           bm25(wiki_fts) as score,
                           highlight(wiki_fts, 0, '<mark>', '</mark>') as title_highlight,
                           snippet(wiki_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
                    FROM wiki_fts
                    WHERE wiki_fts MATCH ?
                    AND branch = ?
                    ORDER BY score
                    LIMIT ? OFFSET ?
                """
                cursor = conn.execute(sql, (fts_query, branch, limit, offset))
            else:
                sql = """
                    SELECT id, title, branch, summary,
                           bm25(wiki_fts) as score,
                           highlight(wiki_fts, 0, '<mark>', '</mark>') as title_highlight,
                           snippet(wiki_fts, 2, '<mark>', '</mark>', '...', 32) as snippet
                    FROM wiki_fts
                    WHERE wiki_fts MATCH ?
                    ORDER BY score
                    LIMIT ? OFFSET ?
                """
                cursor = conn.execute(sql, (fts_query, limit, offset))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "title": row["title"],
                    "branch": row["branch"],
                    "summary": row["summary"],
                    "score": row["score"],
                    "title_highlight": row["title_highlight"],
                    "snippet": row["snippet"],
                })

            return results
        except sqlite3.Error as e:
            raise SearchError(f"Search failed: {e}")
        finally:
            conn.close()

    def _build_fts_query(self, query: str) -> str:
        """
        Build an FTS5-compatible query from user input.

        Handles:
        - Simple word queries
        - Quoted phrases
        - Boolean AND/OR
        """
        query = query.strip()

        # If already has FTS operators, pass through
        if any(op in query.upper() for op in ["AND", "OR", "NOT", '"', "*"]):
            return query

        # Handle quoted phrases
        if '"' in query:
            return query

        # Simple word query - add wildcard for prefix matching
        words = query.split()
        if len(words) == 1:
            return f'"{words[0]}"*'

        # Multiple words - AND them together
        return " ".join(f'"{w}"*' for w in words)

    def rebuild_index(self, nodes: list[WikiNode]) -> None:
        """Rebuild the entire search index from a list of nodes."""
        conn = self._get_connection()
        try:
            # Clear existing index
            conn.execute("DELETE FROM wiki_fts")
            conn.execute("DELETE FROM wiki_fts_meta")
            conn.commit()

            # Re-index all nodes
            for node in nodes:
                self.index_node(node)
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Get search index statistics."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as count FROM wiki_fts")
            doc_count = cursor.fetchone()["count"]

            cursor = conn.execute("SELECT COUNT(*) as count FROM wiki_fts_meta")
            meta_count = cursor.fetchone()["count"]

            return {
                "document_count": doc_count,
                "meta_count": meta_count,
                "db_path": str(self.db_path),
            }
        finally:
            conn.close()
