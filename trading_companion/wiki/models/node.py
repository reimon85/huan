"""WikiNode data model - immutable representation of a knowledge unit."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, FrozenSet
from uuid import UUID, uuid4


class NodeType(Enum):
    """Types of wiki nodes."""

    BRANCH_ROOT = "branch_root"
    TOPIC = "topic"
    ARTICLE = "article"
    CONCEPT = "concept"


@dataclass(frozen=True)
class WikiNode:
    """
    Immutable wiki node representing a unit of knowledge.

    Attributes:
        id: Unique identifier (UUID)
        title: Human-readable title
        node_type: Type of node (branch, topic, article, concept)
        branch: Which main branch this belongs to
        parent_id: Parent node UUID (None for root branches)
        content: Markdown content (for articles/concepts)
        summary: Brief description for search results
        tags: Associated tags for cross-referencing
        related_nodes: UUIDs of related nodes
        metadata: Additional structured data
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        version: Content version for caching
    """

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    node_type: NodeType = NodeType.ARTICLE
    branch: Optional[str] = None
    parent_id: Optional[UUID] = None
    content: str = ""
    summary: str = ""
    tags: FrozenSet[str] = field(default_factory=frozenset)
    related_nodes: FrozenSet[UUID] = field(default_factory=frozenset)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def with_updates(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[FrozenSet[str]] = None,
        related_nodes: Optional[FrozenSet[UUID]] = None,
        metadata: Optional[dict] = None,
    ) -> "WikiNode":
        """
        Create a new WikiNode with specified updates (immutable pattern).

        Returns a new instance with the changes applied, never mutates.
        """
        return WikiNode(
            id=self.id,
            title=title if title is not None else self.title,
            node_type=self.node_type,
            branch=self.branch,
            parent_id=self.parent_id,
            content=content if content is not None else self.content,
            summary=summary if summary is not None else self.summary,
            tags=tags if tags is not None else self.tags,
            related_nodes=related_nodes if related_nodes is not None else self.related_nodes,
            metadata=metadata if metadata is not None else self.metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            version=self.version + 1,
        )

    def with_new_id(self) -> "WikiNode":
        """Create a copy with a new UUID (for creating new nodes from templates)."""
        return WikiNode(
            id=uuid4(),
            title=self.title,
            node_type=self.node_type,
            branch=self.branch,
            parent_id=self.parent_id,
            content=self.content,
            summary=self.summary,
            tags=self.tags,
            related_nodes=self.related_nodes,
            metadata=self.metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            version=1,
        )

    def to_searchable_text(self) -> str:
        """Combine all searchable fields into a single text block."""
        parts = [self.title, self.summary, self.content]
        if self.tags:
            parts.append(" ".join(self.tags))
        return " ".join(parts)
