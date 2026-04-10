"""Unit tests for wiki models."""

import pytest
from datetime import datetime
from uuid import uuid4

from trading_companion.wiki.models import WikiNode, WikiBranch, NodeType


class TestWikiNode:
    """Tests for WikiNode model."""

    def test_create_minimal_node(self) -> None:
        """Test creating a node with minimal fields."""
        node = WikiNode(title="Test Node")

        assert node.title == "Test Node"
        assert node.node_type == NodeType.ARTICLE
        assert node.branch is None
        assert node.content == ""
        assert node.version == 1

    def test_create_full_node(self) -> None:
        """Test creating a node with all fields."""
        node_id = uuid4()
        parent_id = uuid4()
        now = datetime.utcnow()

        node = WikiNode(
            id=node_id,
            title="Full Node",
            node_type=NodeType.ARTICLE,
            branch="trading",
            parent_id=parent_id,
            content="# Test Content",
            summary="A test node",
            tags=frozenset(["test", "example"]),
            related_nodes=frozenset([uuid4()]),
            metadata={"key": "value"},
            created_at=now,
            updated_at=now,
            version=1,
        )

        assert node.id == node_id
        assert node.title == "Full Node"
        assert node.branch == "trading"
        assert node.parent_id == parent_id
        assert "test" in node.tags
        assert node.metadata["key"] == "value"

    def test_node_is_frozen(self) -> None:
        """Test that WikiNode is immutable (frozen)."""
        node = WikiNode(title="Original")

        with pytest.raises(AttributeError):
            node.title = "Modified"  # type: ignore

    def test_with_updates_returns_new_node(self) -> None:
        """Test that with_updates creates a new instance."""
        original = WikiNode(
            title="Original",
            content="Original content",
            version=1,
        )

        updated = original.with_updates(title="Updated", content="New content")

        # Original should be unchanged
        assert original.title == "Original"
        assert original.content == "Original content"

        # Updated should have new values
        assert updated.title == "Updated"
        assert updated.content == "New content"

        # Version should increment
        assert updated.version == 2

    def test_with_updates_partial(self) -> None:
        """Test partial updates with with_updates."""
        node = WikiNode(title="Original", content="Content", summary="Summary")

        updated = node.with_updates(summary="New summary")

        assert updated.title == "Original"
        assert updated.content == "Content"
        assert updated.summary == "New summary"

    def test_with_new_id(self) -> None:
        """Test creating a copy with a new ID."""
        original = WikiNode(title="Test", branch="trading")
        original_id = original.id

        copy = original.with_new_id()

        assert copy.id != original_id
        assert copy.title == original.title
        assert copy.branch == original.branch
        assert copy.version == 1

    def test_to_searchable_text(self) -> None:
        """Test combining searchable fields."""
        node = WikiNode(
            title="Trading Basics",
            content="Price action is fundamental",
            summary="Introduction to trading",
            tags=frozenset(["basics", "trading"]),
        )

        text = node.to_searchable_text()

        assert "Trading Basics" in text
        assert "Price action" in text
        assert "Introduction" in text
        assert "basics" in text
        assert "trading" in text


class TestWikiBranch:
    """Tests for WikiBranch enum."""

    def test_all_branches_have_values(self) -> None:
        """Test all 6 branches exist."""
        assert len(WikiBranch) == 6
        assert WikiBranch.TRADING in WikiBranch
        assert WikiBranch.TRADING_SYSTEMS in WikiBranch
        assert WikiBranch.DATA_ANALYSIS in WikiBranch
        assert WikiBranch.TRADING_BOTS in WikiBranch
        assert WikiBranch.PSICOLOGIA_TRADING in WikiBranch
        assert WikiBranch.REGULACION in WikiBranch

    def test_display_names(self) -> None:
        """Test display names are human-readable."""
        assert WikiBranch.TRADING.display_name == "Trading"
        assert WikiBranch.TRADING_SYSTEMS.display_name == "Trading Systems"
        assert WikiBranch.PSICOLOGIA_TRADING.display_name == "Psicología Trading"

    def test_subtopics(self) -> None:
        """Test that branches have subtopics."""
        assert len(WikiBranch.TRADING.subtopics) > 0
        assert "Fundamentos" in WikiBranch.TRADING.subtopics
        assert len(WikiBranch.TRADING_SYSTEMS.subtopics) > 0


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_types(self) -> None:
        """Test all node types exist."""
        assert NodeType.BRANCH_ROOT in NodeType
        assert NodeType.TOPIC in NodeType
        assert NodeType.ARTICLE in NodeType
        assert NodeType.CONCEPT in NodeType
