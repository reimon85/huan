"""Core wiki service - CRUD operations and business logic."""

from typing import Optional
from uuid import UUID

from trading_companion.core.exceptions import (
    NodeNotFoundError,
    DuplicateNodeError,
    InvalidNodeError,
)
from trading_companion.wiki.models import WikiNode, WikiBranch, NodeType
from trading_companion.wiki.repository import WikiRepository
from trading_companion.wiki.repository.search_index import SearchIndex


class WikiService:
    """
    Core wiki service handling CRUD operations.

    Provides the main interface for creating, reading, updating,
    and deleting wiki nodes, with integrated search indexing.
    """

    def __init__(self, repository: WikiRepository, search_index: SearchIndex) -> None:
        self.repository = repository
        self.search_index = search_index

    def create_node(
        self,
        title: str,
        content: str,
        branch: WikiBranch,
        node_type: NodeType = NodeType.ARTICLE,
        parent_id: Optional[UUID] = None,
        summary: str = "",
        tags: Optional[frozenset[str]] = None,
        metadata: Optional[dict] = None,
    ) -> WikiNode:
        """
        Create a new wiki node.

        Args:
            title: Node title
            content: Markdown content
            branch: Wiki branch this node belongs to
            node_type: Type of node (article, concept, etc.)
            parent_id: Optional parent node UUID
            summary: Brief description for search results
            tags: Optional set of tags
            metadata: Optional additional metadata

        Returns:
            The created WikiNode

        Raises:
            DuplicateNodeError: If a node with same title exists in branch
        """
        # Check for duplicates
        if self.repository.exists_by_title(title, branch):
            raise DuplicateNodeError(title, branch.value)

        # Validate parent exists if provided
        if parent_id:
            parent = self.repository.get_by_id(str(parent_id))
            if not parent:
                raise NodeNotFoundError(str(parent_id))

        # Create node (immutable pattern - all args via constructor)
        node = WikiNode(
            title=title,
            content=content,
            node_type=node_type,
            branch=branch.value,
            parent_id=parent_id,
            summary=summary,
            tags=tags or frozenset(),
            metadata=metadata or {},
        )

        # Save to repository
        saved_node = self.repository.save(node)

        # Index for search
        self.search_index.index_node(saved_node)

        return saved_node

    def get_node(self, node_id: str) -> WikiNode:
        """
        Get a wiki node by ID.

        Args:
            node_id: UUID string of the node

        Returns:
            The WikiNode

        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        node = self.repository.get_by_id(node_id)
        if not node:
            raise NodeNotFoundError(node_id)
        return node

    def update_node(
        self,
        node_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[frozenset[str]] = None,
        metadata: Optional[dict] = None,
    ) -> WikiNode:
        """
        Update an existing wiki node.

        Args:
            node_id: UUID string of the node to update
            title: New title (optional)
            content: New content (optional)
            summary: New summary (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)

        Returns:
            The updated WikiNode (new instance, immutable)

        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        node = self.get_node(node_id)

        # Create new node with updates (immutable pattern)
        updated_node = node.with_updates(
            title=title,
            content=content,
            summary=summary,
            tags=tags,
            metadata=metadata,
        )

        # Save updated node
        saved_node = self.repository.save(updated_node)

        # Re-index for search
        self.search_index.index_node(saved_node)

        return saved_node

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a wiki node.

        Args:
            node_id: UUID string of the node to delete

        Returns:
            True if deleted

        Raises:
            NodeNotFoundError: If node doesn't exist
        """
        node = self.get_node(node_id)

        # Check for children
        children = self.repository.get_children(node_id)
        if children:
            raise InvalidNodeError(
                f"Cannot delete node with {len(children)} children. Delete children first."
            )

        # Remove from search index
        self.search_index.remove_node(node.id)

        # Delete from repository
        return self.repository.delete(node_id)

    def get_branch_tree(self, branch: WikiBranch) -> dict:
        """
        Get the full tree structure for a branch.

        Returns:
            Nested dictionary representing the branch structure
        """
        nodes = self.repository.get_by_branch(branch)

        # Build tree structure
        root_nodes = [n for n in nodes if n.parent_id is None]
        tree = {
            "branch": branch.value,
            "display_name": branch.display_name,
            "subtopics": branch.subtopics,
            "nodes": [self._node_to_dict(n) for n in root_nodes],
        }

        return tree

    def get_children(self, node_id: str) -> list[WikiNode]:
        """Get direct children of a node."""
        return self.repository.get_children(node_id)

    def get_all_branches(self) -> list[dict]:
        """Get summary info for all branches."""
        return [
            {
                "value": branch.value,
                "display_name": branch.display_name,
                "subtopics": branch.subtopics,
            }
            for branch in WikiBranch
        ]

    def _node_to_dict(self, node: WikiNode) -> dict:
        """Convert node to dictionary representation."""
        return {
            "id": str(node.id),
            "title": node.title,
            "node_type": node.node_type.value,
            "branch": node.branch,
            "summary": node.summary,
            "tags": list(node.tags),
            "version": node.version,
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
        }
