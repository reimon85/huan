"""Repository layer for wiki storage and retrieval."""

from abc import ABC, abstractmethod
from typing import Optional

from trading_companion.wiki.models import WikiNode, WikiBranch


class WikiRepository(ABC):
    """Abstract repository interface for wiki node storage."""

    @abstractmethod
    def get_by_id(self, node_id: str) -> Optional[WikiNode]:
        """Retrieve a node by its UUID."""
        pass

    @abstractmethod
    def save(self, node: WikiNode) -> WikiNode:
        """Save or update a node. Returns the saved node."""
        pass

    @abstractmethod
    def delete(self, node_id: str) -> bool:
        """Delete a node by its UUID. Returns True if deleted."""
        pass

    @abstractmethod
    def get_by_branch(self, branch: WikiBranch) -> list[WikiNode]:
        """Get all nodes in a specific branch."""
        pass

    @abstractmethod
    def get_children(self, parent_id: str) -> list[WikiNode]:
        """Get all direct children of a node."""
        pass

    @abstractmethod
    def get_root_nodes(self) -> list[WikiNode]:
        """Get all root (top-level) nodes for each branch."""
        pass

    @abstractmethod
    def exists(self, node_id: str) -> bool:
        """Check if a node exists."""
        pass

    @abstractmethod
    def exists_by_title(self, title: str, branch: WikiBranch) -> bool:
        """Check if a node with given title exists in branch."""
        pass
