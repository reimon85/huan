"""Integration tests for wiki API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from trading_companion.main import app
from trading_companion.wiki.models import WikiBranch, NodeType


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all wiki services for API testing."""
    with patch("trading_companion.wiki.api.wiki_api.get_wiki_service") as mock_wiki, \
         patch("trading_companion.wiki.api.wiki_api.get_query_service") as mock_query, \
         patch("trading_companion.wiki.api.wiki_api.get_graph_service") as mock_graph:

        yield {
            "wiki": mock_wiki,
            "query": mock_query,
            "graph": mock_graph,
        }


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health endpoint returns healthy status."""
        response = client.get("/api/v1/wiki/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestBranchEndpoints:
    """Tests for branch-related endpoints."""

    def test_list_branches(self, client: TestClient, mock_services: dict) -> None:
        """Test listing all branches."""
        mock_wiki = MagicMock()
        mock_wiki.get_all_branches.return_value = [
            {"value": "trading", "display_name": "Trading", "subtopics": ["Fundamentos"]},
            {"value": "trading_systems", "display_name": "Trading Systems", "subtopics": []},
        ]
        mock_services["wiki"].return_value = mock_wiki

        response = client.get("/api/v1/wiki/branches")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["value"] == "trading"

    def test_get_branch_tree(self, client: TestClient, mock_services: dict) -> None:
        """Test getting a specific branch tree."""
        mock_wiki = MagicMock()
        mock_wiki.get_branch_tree.return_value = {
            "branch": "trading",
            "display_name": "Trading",
            "subtopics": ["Fundamentos", "Análisis Técnico"],
            "nodes": [],
        }
        mock_services["wiki"].return_value = mock_wiki

        response = client.get("/api/v1/wiki/branches/trading/tree")

        assert response.status_code == 200
        data = response.json()
        assert data["branch"] == "trading"


class TestNodeEndpoints:
    """Tests for node-related endpoints."""

    def test_create_node(self, client: TestClient, mock_services: dict) -> None:
        """Test creating a new node."""
        from uuid import uuid4
        from trading_companion.wiki.models import WikiNode

        mock_node = WikiNode(
            id=uuid4(),
            title="New Strategy",
            content="# Strategy\n\nContent",
            node_type=NodeType.ARTICLE,
            branch="trading",
            summary="A new strategy",
            tags=frozenset(["strategy"]),
        )

        mock_wiki = MagicMock()
        mock_wiki.create_node.return_value = mock_node
        mock_services["wiki"].return_value = mock_wiki

        response = client.post(
            "/api/v1/wiki/nodes",
            json={
                "title": "New Strategy",
                "content": "# Strategy\n\nContent",
                "branch": "trading",
                "summary": "A new strategy",
                "tags": ["strategy"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Strategy"

    def test_get_node(self, client: TestClient, mock_services: dict) -> None:
        """Test getting a node by ID."""
        from uuid import uuid4
        from trading_companion.wiki.models import WikiNode

        node_id = uuid4()
        mock_node = WikiNode(
            id=node_id,
            title="Test Node",
            content="Content",
            node_type=NodeType.ARTICLE,
            branch="trading",
        )

        mock_wiki = MagicMock()
        mock_wiki.get_node.return_value = mock_node
        mock_services["wiki"].return_value = mock_wiki

        response = client.get(f"/api/v1/wiki/nodes/{node_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Node"

    def test_get_node_not_found(self, client: TestClient, mock_services: dict) -> None:
        """Test getting a non-existent node returns 404."""
        from trading_companion.core.exceptions import NodeNotFoundError

        mock_wiki = MagicMock()
        mock_wiki.get_node.side_effect = NodeNotFoundError("nonexistent-id")
        mock_services["wiki"].return_value = mock_wiki

        response = client.get("/api/v1/wiki/nodes/nonexistent-id")

        assert response.status_code == 404

    def test_update_node(self, client: TestClient, mock_services: dict) -> None:
        """Test updating a node."""
        from uuid import uuid4
        from trading_companion.wiki.models import WikiNode

        node_id = uuid4()
        mock_node = WikiNode(
            id=node_id,
            title="Updated Title",
            content="Updated content",
            node_type=NodeType.ARTICLE,
            branch="trading",
            version=2,
        )

        mock_wiki = MagicMock()
        mock_wiki.update_node.return_value = mock_node
        mock_services["wiki"].return_value = mock_wiki

        response = client.put(
            f"/api/v1/wiki/nodes/{node_id}",
            json={"title": "Updated Title", "content": "Updated content"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_node(self, client: TestClient, mock_services: dict) -> None:
        """Test deleting a node."""
        from uuid import uuid4

        mock_wiki = MagicMock()
        mock_wiki.delete_node.return_value = True
        mock_services["wiki"].return_value = mock_wiki

        response = client.delete(f"/api/v1/wiki/nodes/{uuid4()}")

        assert response.status_code == 204


class TestSearchEndpoints:
    """Tests for search endpoints."""

    def test_search(self, client: TestClient, mock_services: dict) -> None:
        """Test searching wiki content."""
        mock_query = MagicMock()
        mock_query.search.return_value = {
            "query": "RSI",
            "results": [
                {
                    "id": "123",
                    "title": "RSI Indicator",
                    "branch": "data_analysis",
                    "summary": "Momentum oscillator",
                    "score": 1.5,
                    "title_highlight": "<mark>RSI</mark> Indicator",
                    "snippet": "The Relative Strength Index...",
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        }
        mock_services["query"].return_value = mock_query

        response = client.get("/api/v1/wiki/search?q=RSI")

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "RSI"
        assert len(data["results"]) == 1
        assert "RSI" in data["results"][0]["title"]

    def test_search_with_branch_filter(self, client: TestClient, mock_services: dict) -> None:
        """Test search with branch filter."""
        mock_query = MagicMock()
        mock_query.search.return_value = {
            "query": "strategy",
            "results": [],
            "total": 0,
            "limit": 20,
            "offset": 0,
        }
        mock_services["query"].return_value = mock_query

        response = client.get("/api/v1/wiki/search?q=strategy&branch=trading")

        assert response.status_code == 200

    def test_list_tags(self, client: TestClient, mock_services: dict) -> None:
        """Test listing all tags."""
        mock_query = MagicMock()
        mock_query.get_all_tags.return_value = ["strategy", "technical", "analysis"]
        mock_services["query"].return_value = mock_query

        response = client.get("/api/v1/wiki/tags")

        assert response.status_code == 200
        data = response.json()
        assert "strategy" in data


class TestStatsEndpoints:
    """Tests for statistics endpoints."""

    def test_get_stats(self, client: TestClient, mock_services: dict) -> None:
        """Test getting wiki statistics."""
        mock_query = MagicMock()
        mock_query.get_node_count_by_branch.return_value = {
            "trading": 5,
            "trading_systems": 3,
        }
        mock_query.get_recent_nodes.return_value = []
        mock_services["query"].return_value = mock_query

        # Mock search index
        with patch("trading_companion.wiki.api.wiki_api.SearchIndex") as mock_index_class:
            mock_index = MagicMock()
            mock_index.get_stats.return_value = {"document_count": 8, "db_path": ":memory:"}
            mock_index_class.return_value = mock_index

            response = client.get("/api/v1/wiki/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_nodes"] == 8
