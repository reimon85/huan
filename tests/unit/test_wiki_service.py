"""Unit tests for wiki services."""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from trading_companion.wiki.models import WikiNode, WikiBranch, NodeType
from trading_companion.wiki.services import WikiService, QueryService, KnowledgeGraphService
from trading_companion.wiki.repository import WikiRepository
from trading_companion.wiki.repository.search_index import SearchIndex
from trading_companion.core.exceptions import NodeNotFoundError, DuplicateNodeError


class MockWikiRepository(WikiRepository):
    """Mock implementation of WikiRepository for testing."""

    def __init__(self) -> None:
        self._nodes: dict[str, WikiNode] = {}

    def get_by_id(self, node_id: str) -> WikiNode | None:
        return self._nodes.get(node_id)

    def save(self, node: WikiNode) -> WikiNode:
        self._nodes[str(node.id)] = node
        return node

    def delete(self, node_id: str) -> bool:
        if node_id in self._nodes:
            del self._nodes[node_id]
            return True
        return False

    def get_by_branch(self, branch: WikiBranch) -> list[WikiNode]:
        return [n for n in self._nodes.values() if n.branch == branch.value]

    def get_children(self, parent_id: str) -> list[WikiNode]:
        return [n for n in self._nodes.values() if n.parent_id and str(n.parent_id) == parent_id]

    def get_root_nodes(self) -> list[WikiNode]:
        return [n for n in self._nodes.values() if n.parent_id is None]

    def exists(self, node_id: str) -> bool:
        return node_id in self._nodes

    def exists_by_title(self, title: str, branch: WikiBranch) -> bool:
        return any(
            n.title.lower() == title.lower() and n.branch == branch.value
            for n in self._nodes.values()
        )


class MockSearchIndex:
    """Mock search index for testing."""

    def __init__(self) -> None:
        self._indexed: list[WikiNode] = []

    def index_node(self, node: WikiNode) -> None:
        if node not in self._indexed:
            self._indexed.append(node)

    def remove_node(self, node_id: uuid4) -> None:
        self._indexed = [n for n in self._indexed if str(n.id) != str(node_id)]

    def search(
        self, query: str, branch: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        results = []
        for node in self._indexed:
            if query.lower() in node.title.lower() or query.lower() in node.content.lower():
                if branch is None or node.branch == branch:
                    results.append({
                        "id": str(node.id),
                        "title": node.title,
                        "branch": node.branch,
                        "summary": node.summary,
                        "score": 1.0,
                        "title_highlight": node.title,
                        "snippet": node.summary[:50],
                    })
        return results


class TestWikiService:
    """Tests for WikiService."""

    @pytest.fixture
    def repository(self) -> MockWikiRepository:
        return MockWikiRepository()

    @pytest.fixture
    def search_index(self) -> MockSearchIndex:
        return MockSearchIndex()

    @pytest.fixture
    def service(self, repository: MockWikiRepository, search_index: MockSearchIndex) -> WikiService:
        return WikiService(repository, search_index)

    def test_create_node(self, service: WikiService) -> None:
        """Test creating a new node."""
        node = service.create_node(
            title="Test Trading Strategy",
            content="# Strategy\n\nThis is a test strategy.",
            branch=WikiBranch.TRADING,
            summary="A testing strategy",
            tags=frozenset(["test", "strategy"]),
        )

        assert node.title == "Test Trading Strategy"
        assert node.branch == "trading"
        assert node.node_type == NodeType.ARTICLE
        assert "test" in node.tags

    def test_create_node_duplicate_raises_error(self, service: WikiService) -> None:
        """Test that creating a duplicate node raises an error."""
        service.create_node(
            title="Duplicate Test",
            content="Content",
            branch=WikiBranch.TRADING,
        )

        with pytest.raises(DuplicateNodeError):
            service.create_node(
                title="Duplicate Test",
                content="Different content",
                branch=WikiBranch.TRADING,
            )

    def test_get_node(self, service: WikiService) -> None:
        """Test retrieving a node by ID."""
        created = service.create_node(
            title="Get Test",
            content="Content",
            branch=WikiBranch.TRADING,
        )

        retrieved = service.get_node(str(created.id))

        assert retrieved.id == created.id
        assert retrieved.title == "Get Test"

    def test_get_node_not_found(self, service: WikiService) -> None:
        """Test that getting a non-existent node raises an error."""
        with pytest.raises(NodeNotFoundError):
            service.get_node(str(uuid4()))

    def test_update_node(self, service: WikiService) -> None:
        """Test updating a node."""
        original = service.create_node(
            title="Original Title",
            content="Original content",
            branch=WikiBranch.TRADING,
        )

        updated = service.update_node(
            node_id=str(original.id),
            title="Updated Title",
            content="Updated content",
        )

        assert updated.title == "Updated Title"
        assert updated.content == "Updated content"
        assert updated.version == 2

        # Original should be unchanged
        assert original.title == "Original Title"

    def test_delete_node(self, service: WikiService) -> None:
        """Test deleting a node."""
        node = service.create_node(
            title="To Delete",
            content="Content",
            branch=WikiBranch.TRADING,
        )

        result = service.delete_node(str(node.id))

        assert result is True
        with pytest.raises(NodeNotFoundError):
            service.get_node(str(node.id))

    def test_get_branch_tree(self, service: WikiService) -> None:
        """Test getting branch tree structure."""
        service.create_node(
            title="Trading Root",
            content="Content",
            branch=WikiBranch.TRADING,
        )

        tree = service.get_branch_tree(WikiBranch.TRADING)

        assert tree["branch"] == "trading"
        assert tree["display_name"] == "Trading"
        assert "Fundamentos" in tree["subtopics"]

    def test_get_all_branches(self, service: WikiService) -> None:
        """Test getting all branches summary."""
        branches = service.get_all_branches()

        assert len(branches) == 6
        assert any(b["value"] == "trading" for b in branches)
        assert any(b["value"] == "trading_systems" for b in branches)


class TestQueryService:
    """Tests for QueryService."""

    @pytest.fixture
    def repository(self) -> MockWikiRepository:
        return MockWikiRepository()

    @pytest.fixture
    def search_index(self) -> MockSearchIndex:
        return MockSearchIndex()

    @pytest.fixture
    def query_service(self, repository: MockWikiRepository, search_index: MockSearchIndex) -> QueryService:
        return QueryService(repository, search_index)

    def test_search_empty_query(self, query_service: QueryService) -> None:
        """Test search with empty query returns empty results."""
        result = query_service.search("")

        assert result["results"] == []
        assert result["total"] == 0

    def test_search_with_results(self, query_service: QueryService, repository: MockWikiRepository, search_index: MockSearchIndex) -> None:
        """Test search returns matching nodes."""
        # Manually index a node for testing
        node = WikiNode(
            title="RSI Indicator",
            content="The Relative Strength Index is a momentum oscillator",
            branch="data_analysis",
            summary="Momentum oscillator",
        )
        repository.save(node)
        search_index.index_node(node)

        result = query_service.search("RSI")

        assert result["total"] >= 1
        assert any("RSI" in r["title"] for r in result["results"])

    def test_get_node_count_by_branch(self, query_service: QueryService, repository: MockWikiRepository) -> None:
        """Test getting node counts per branch."""
        repository.save(WikiNode(title="Node 1", branch="trading"))
        repository.save(WikiNode(title="Node 2", branch="trading"))
        repository.save(WikiNode(title="Node 3", branch="data_analysis"))

        counts = query_service.get_node_count_by_branch()

        assert counts["trading"] == 2
        assert counts["data_analysis"] == 1


class TestKnowledgeGraphService:
    """Tests for KnowledgeGraphService."""

    @pytest.fixture
    def repository(self) -> MockWikiRepository:
        return MockWikiRepository()

    @pytest.fixture
    def graph_service(self, repository: MockWikiRepository) -> KnowledgeGraphService:
        return KnowledgeGraphService(repository)

    def test_build_graph(self, graph_service: KnowledgeGraphService) -> None:
        """Test building the knowledge graph."""
        # Create some nodes
        root = WikiNode(title="Trading Root", branch="trading")
        self.repository.save(root)

        child = WikiNode(
            title="Child Node",
            branch="trading",
            parent_id=root.id,
        )
        self.repository.save(child)

        graph = graph_service.build_graph()

        assert graph is not None
        assert graph.number_of_nodes() >= 2

    def test_get_related_nodes_empty(self, graph_service: KnowledgeGraphService) -> None:
        """Test getting related nodes for a node with no relationships."""
        result = graph_service.get_related_nodes(str(uuid4()))
        assert result == []
