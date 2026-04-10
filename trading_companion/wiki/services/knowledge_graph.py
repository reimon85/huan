"""Knowledge graph service - node relationships and traversal."""

from typing import Optional

import networkx as nx

from trading_companion.wiki.models import WikiNode, RelationshipType
from trading_companion.wiki.repository import WikiRepository


class KnowledgeGraphService:
    """
    Service for managing and traversing node relationships.

    Builds a graph from wiki nodes and provides traversal
    operations for finding related concepts.
    """

    def __init__(self, repository: WikiRepository) -> None:
        self.repository = repository
        self._graph: Optional[nx.DiGraph] = None

    def build_graph(self) -> nx.DiGraph:
        """
        Build a NetworkX graph from all wiki nodes.

        Returns:
            The constructed graph
        """
        self._graph = nx.DiGraph()

        # Add all nodes to graph
        for branch in self.repository.get_root_nodes():
            self._add_node_to_graph(branch)

        # Build edges from relationships
        for branch in WikiBranch.__members__.values():
            nodes = self.repository.get_by_branch(branch)
            for node in nodes:
                if node.parent_id:
                    self._graph.add_edge(
                        node.parent_id,
                        node.id,
                        relationship=RelationshipType.PARENT_OF.value,
                    )

                for related_id in node.related_nodes:
                    self._graph.add_edge(
                        node.id,
                        related_id,
                        relationship=RelationshipType.RELATED_TO.value,
                    )

        return self._graph

    def _add_node_to_graph(self, node: WikiNode) -> None:
        """Add a single node and its children to the graph."""
        self._graph.add_node(
            node.id,
            title=node.title,
            branch=node.branch,
            node_type=node.node_type.value,
        )

        children = self.repository.get_children(str(node.id))
        for child in children:
            self._add_node_to_graph(child)

    def get_related_nodes(
        self, node_id: str, max_depth: int = 2, relationship_type: Optional[RelationshipType] = None
    ) -> list[dict]:
        """
        Find nodes related to the given node through graph traversal.

        Args:
            node_id: UUID of the starting node
            max_depth: Maximum traversal depth
            relationship_type: Optional filter by relationship type

        Returns:
            List of related nodes with path information
        """
        if self._graph is None:
            self.build_graph()

        try:
            source_id = node_id
            related = []

            # BFS traversal
            visited = {source_id}
            queue = [(source_id, 0, [])]

            while queue:
                current_id, depth, path = queue.pop(0)

                if depth > max_depth:
                    continue

                # Get neighbors
                successors = self._graph.successors(current_id)
                predecessors = self._graph.predecessors(current_id)

                for neighbor in list(successors) + list(predecessors):
                    if neighbor not in visited:
                        visited.add(neighbor)

                        edge_data = self._graph.get_edge_data(current_id, neighbor)
                        rel_type = edge_data.get("relationship", "related_to") if edge_data else "related_to"

                        if relationship_type is None or rel_type == relationship_type.value:
                            node_data = self._graph.nodes[neighbor]
                            related.append({
                                "id": str(neighbor),
                                "title": node_data.get("title", ""),
                                "branch": node_data.get("branch", ""),
                                "relationship": rel_type,
                                "depth": depth + 1,
                                "path": path + [current_id],
                            })

                        queue.append((neighbor, depth + 1, path + [current_id]))

            return related
        except nx.NetworkXError:
            return []

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[list[str]]:
        """
        Find the shortest path between two nodes.

        Args:
            source_id: Starting node UUID
            target_id: Ending node UUID

        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if self._graph is None:
            self.build_graph()

        try:
            path = nx.shortest_path(self._graph, source_id, target_id)
            return [str(n) for n in path]
        except nx.NetworkXNoPath:
            return None

    def get_subgraph(self, node_id: str, depth: int = 2) -> nx.DiGraph:
        """
        Get a subgraph centered on a node.

        Args:
            node_id: Center node UUID
            depth: Depth of the subgraph

        Returns:
            Subgraph containing nodes within the specified depth
        """
        if self._graph is None:
            self.build_graph()

        return nxego_graph(self._graph, node_id, radius=depth)

    def get_node_degree(self, node_id: str) -> dict:
        """
        Get the degree statistics for a node.

        Args:
            node_id: Node UUID

        Returns:
            Dictionary with in_degree, out_degree, and total degree
        """
        if self._graph is None:
            self.build_graph()

        try:
            return {
                "in_degree": self._graph.in_degree(node_id),
                "out_degree": self._graph.out_degree(node_id),
                "total_degree": self._graph.degree(node_id),
            }
        except nx.NetworkXError:
            return {"in_degree": 0, "out_degree": 0, "total_degree": 0}

    @property
    def graph(self) -> Optional[nx.DiGraph]:
        """Get the current graph, building it if necessary."""
        if self._graph is None:
            self.build_graph()
        return self._graph


# Helper function since nx.ego_graph isn't a direct function
def nxego_graph(G: nx.DiGraph, node: str, radius: int) -> nx.DiGraph:
    """Get ego graph centered on a node."""
    return nx.ego_graph(G, node, radius=radius)


from trading_companion.wiki.models import WikiBranch
