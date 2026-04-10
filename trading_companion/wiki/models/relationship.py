"""Node relationship model for knowledge graph connections."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class RelationshipType(Enum):
    """Types of relationships between wiki nodes."""

    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    RELATED_TO = "related_to"
    REFERENCES = "references"
    SEE_ALSO = "see_also"
    PREREQUISITE_FOR = "prerequisite_for"
    BUILT_ON = "built_on"


@dataclass(frozen=True)
class NodeRelationship:
    """
    Immutable relationship between two wiki nodes.

    Attributes:
        id: Unique identifier
        source_id: UUID of the source node
        target_id: UUID of the target node
        relationship_type: Type of relationship
        weight: Optional weight for graph algorithms (0.0 to 1.0)
        description: Human-readable description of the relationship
        created_at: Creation timestamp
    """

    id: UUID = field(default_factory=uuid4)
    source_id: UUID = field(default_factory=uuid4)
    target_id: UUID = field(default_factory=uuid4)
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    weight: float = 1.0
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_directed(self) -> bool:
        """Whether this relationship has a direction (not bidirectional)."""
        return self.relationship_type in (
            RelationshipType.PARENT_OF,
            RelationshipType.CHILD_OF,
            RelationshipType.PREREQUISITE_FOR,
            RelationshipType.BUILT_ON,
            RelationshipType.REFERENCES,
        )
