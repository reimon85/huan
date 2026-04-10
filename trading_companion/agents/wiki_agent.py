"""Wiki Agent - AI agent interface to the wiki knowledge base."""

from typing import Optional

from trading_companion.wiki.models import WikiBranch
from trading_companion.wiki.services import WikiService, QueryService


class WikiAgent:
    """
    AI Agent interface for querying the wiki knowledge base.

    This agent provides a natural language-friendly interface
    to retrieve and synthesize information from the trading wiki.
    """

    def __init__(self, wiki_service: WikiService, query_service: QueryService) -> None:
        self.wiki = wiki_service
        self.query = query_service

    async def get_trading_context(
        self,
        topic: str,
        branch: Optional[WikiBranch] = None,
        limit: int = 5,
    ) -> dict:
        """
        Get relevant trading context for a topic.

        Args:
            topic: The trading topic to query
            branch: Optional branch to filter results
            limit: Maximum number of results

        Returns:
            Dictionary with relevant wiki content
        """
        search_results = self.query.search(
            query=topic,
            branch=branch,
            limit=limit,
        )

        return {
            "query": topic,
            "context": search_results["results"],
            "total_found": search_results["total"],
        }

    async def get_strategy_guidance(
        self,
        strategy_type: str,
        market_conditions: dict,
    ) -> str:
        """
        Get guidance on which strategy to apply.

        Args:
            strategy_type: Type of strategy (trend, mean_reversion, etc.)
            market_conditions: Current market state

        Returns:
            Synthesized guidance from wiki content
        """
        # Get relevant content
        results = self.query.search(
            query=f"{strategy_type} strategy {market_conditions.get('trend', 'sideways')}",
            branch=WikiBranch.TRADING_SYSTEMS,
            limit=3,
        )

        # Synthesize response
        if results["total"] == 0:
            return "No specific guidance found. Consider reviewing general trading principles."

        return self._synthesize_guidance(results["results"])

    async def get_risk_management_checklist(
        self,
        trade_type: str,
    ) -> list[str]:
        """
        Get a risk management checklist for a trade type.

        Args:
            trade_type: Type of trade (day_trade, swing, position)

        Returns:
            List of checklist items
        """
        # Get risk management content
        results = self.query.search(
            query=f"{trade_type} risk management checklist",
            branch=WikiBranch.TRADING,
            limit=5,
        )

        checklist = []
        for result in results["results"]:
            # Extract checklist items from content
            checklist.append(f"- {result['title']}: {result['snippet']}")

        return checklist

    def _synthesize_guidance(self, search_results: list[dict]) -> str:
        """Synthesize multiple search results into coherent guidance."""
        if not search_results:
            return "No relevant information found."

        guidance_parts = []
        for i, result in enumerate(search_results[:3], 1):
            guidance_parts.append(
                f"{i}. **{result['title']}**: {result['snippet']}"
            )

        return "\n\n".join(guidance_parts)

    async def get_related_concepts(
        self,
        concept: str,
        max_depth: int = 2,
    ) -> list[dict]:
        """
        Get related concepts through the knowledge graph.

        Args:
            concept: Central concept to explore
            max_depth: How deep to explore the graph

        Returns:
            List of related concepts with relationship info
        """
        # First find the node
        nodes = self.query.search(query=concept, limit=1)

        if not nodes["results"]:
            return []

        node_id = nodes["results"][0]["id"]

        # Get related through graph service
        # Note: This would use KnowledgeGraphService in production
        return []

    def format_wiki_response(
        self,
        topic: str,
        content: str,
        include_sources: bool = True,
    ) -> str:
        """
        Format wiki content for agent consumption.

        Args:
            topic: The topic being queried
            content: Raw wiki content
            include_sources: Whether to include source attribution

        Returns:
            Formatted response string
        """
        formatted = f"## {topic}\n\n"
        formatted += f"{content}\n\n"

        if include_sources:
            formatted += "---\n"
            formatted += "*Source: Trading Companion Wiki*"

        return formatted
