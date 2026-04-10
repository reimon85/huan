"""Query service - search and retrieval operations."""

from typing import Optional

from trading_companion.wiki.models import WikiBranch
from trading_companion.wiki.repository.search_index import SearchIndex
from trading_companion.wiki.repository import WikiRepository
from trading_companion.core.exceptions import SearchError


class QueryService:
    """
    Service for searching and querying wiki content.

    Provides full-text search, filtering, and aggregations
    across the wiki knowledge base.
    """

    def __init__(self, repository: WikiRepository, search_index: SearchIndex) -> None:
        self.repository = repository
        self.search_index = search_index

    def search(
        self,
        query: str,
        branch: Optional[WikiBranch] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Perform full-text search across wiki content.

        Args:
            query: Search query string
            branch: Optional branch to filter results
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Search results with pagination info
        """
        if not query or not query.strip():
            return {
                "query": query,
                "results": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
            }

        try:
            branch_value = branch.value if branch else None
            results = self.search_index.search(
                query=query,
                branch=branch_value,
                limit=limit,
                offset=offset,
            )

            return {
                "query": query,
                "results": results,
                "total": len(results),
                "limit": limit,
                "offset": offset,
            }
        except SearchError as e:
            raise SearchError(f"Search failed for '{query}': {e}")

    def search_by_tag(self, tag: str, limit: int = 20) -> list[dict]:
        """
        Find all nodes with a specific tag.

        Args:
            tag: Tag to search for
            limit: Maximum results

        Returns:
            List of matching nodes
        """
        # Get all nodes and filter by tag (simple approach)
        # For large wikis, this should be indexed
        all_nodes = []
        for branch in WikiBranch:
            nodes = self.repository.get_by_branch(branch)
            all_nodes.extend(nodes)

        matching = [n for n in all_nodes if tag in n.tags]
        return [
            {
                "id": str(n.id),
                "title": n.title,
                "branch": n.branch,
                "summary": n.summary,
                "tags": list(n.tags),
            }
            for n in matching[:limit]
        ]

    def get_recent_nodes(self, limit: int = 10) -> list[dict]:
        """
        Get recently updated nodes.

        Args:
            limit: Maximum number of results

        Returns:
            List of recently updated nodes
        """
        all_nodes = []
        for branch in WikiBranch:
            nodes = self.repository.get_by_branch(branch)
            all_nodes.extend(nodes)

        # Sort by updated_at descending
        sorted_nodes = sorted(all_nodes, key=lambda n: n.updated_at, reverse=True)

        return [
            {
                "id": str(n.id),
                "title": n.title,
                "branch": n.branch,
                "updated_at": n.updated_at.isoformat(),
            }
            for n in sorted_nodes[:limit]
        ]

    def get_node_count_by_branch(self) -> dict:
        """Get node count for each branch."""
        counts = {}
        for branch in WikiBranch:
            nodes = self.repository.get_by_branch(branch)
            counts[branch.value] = len(nodes)
        return counts

    def get_all_tags(self) -> list[str]:
        """Get all unique tags across the wiki."""
        all_tags = set()
        for branch in WikiBranch:
            nodes = self.repository.get_by_branch(branch)
            for node in nodes:
                all_tags.update(node.tags)
        return sorted(all_tags)
