"""FastAPI REST API for wiki operations."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from trading_companion.core.exceptions import (
    NodeNotFoundError,
    DuplicateNodeError,
    InvalidNodeError,
)
from trading_companion.wiki.models import WikiBranch, NodeType
from trading_companion.wiki.services import WikiService, QueryService, KnowledgeGraphService
from trading_companion.wiki.repository import WikiRepository
from trading_companion.wiki.repository.markdown_store import MarkdownStore
from trading_companion.wiki.repository.search_index import SearchIndex


router = APIRouter(prefix="/api/v1/wiki", tags=["wiki"])


def get_wiki_service() -> WikiService:
    """Dependency injection for WikiService."""
    repository = MarkdownStore()
    search_index = SearchIndex()
    return WikiService(repository, search_index)


def get_query_service() -> QueryService:
    """Dependency injection for QueryService."""
    repository = MarkdownStore()
    search_index = SearchIndex()
    return QueryService(repository, search_index)


def get_graph_service() -> KnowledgeGraphService:
    """Dependency injection for KnowledgeGraphService."""
    repository = MarkdownStore()
    return KnowledgeGraphService(repository)


# Request/Response Models
from pydantic import BaseModel, Field


class CreateNodeRequest(BaseModel):
    """Request model for creating a new wiki node."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(default="")
    branch: WikiBranch
    node_type: NodeType = NodeType.ARTICLE
    parent_id: Optional[str] = None
    summary: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class UpdateNodeRequest(BaseModel):
    """Request model for updating a wiki node."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None


class NodeResponse(BaseModel):
    """Response model for a wiki node."""

    id: str
    title: str
    node_type: str
    branch: Optional[str]
    content: str
    summary: str
    tags: list[str]
    parent_id: Optional[str]
    related_nodes: list[str]
    metadata: dict
    version: int
    created_at: str
    updated_at: str


class BranchSummary(BaseModel):
    """Summary info for a wiki branch."""

    value: str
    display_name: str
    subtopics: list[str]


class SearchResult(BaseModel):
    """Single search result."""

    id: str
    title: str
    branch: str
    summary: str
    score: float
    title_highlight: str
    snippet: str


class SearchResponse(BaseModel):
    """Response model for search results."""

    query: str
    results: list[SearchResult]
    total: int
    limit: int
    offset: int


# Endpoints
@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "wiki-api"}


@router.get("/branches", response_model=list[BranchSummary])
async def list_branches() -> list[BranchSummary]:
    """Get all available wiki branches."""
    service = get_wiki_service()
    branches = service.get_all_branches()
    return [BranchSummary(**b) for b in branches]


@router.get("/branches/{branch}/tree")
async def get_branch_tree(branch: WikiBranch) -> dict:
    """Get the full tree structure for a branch."""
    service = get_wiki_service()
    return service.get_branch_tree(branch)


@router.get("/nodes", response_model=list[NodeResponse])
async def list_nodes(
    branch: Optional[WikiBranch] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[NodeResponse]:
    """List wiki nodes, optionally filtered by branch."""
    service = get_wiki_service()
    query_service = get_query_service()

    if branch:
        tree = service.get_branch_tree(branch)
        nodes_data = tree.get("nodes", [])
    else:
        # Get all nodes from all branches
        nodes_data = []
        for b in WikiBranch:
            tree = service.get_branch_tree(b)
            nodes_data.extend(tree.get("nodes", []))

    return [NodeResponse(**n) for n in nodes_data[offset : offset + limit]]


@router.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str) -> NodeResponse:
    """Get a single wiki node by ID."""
    service = get_wiki_service()
    try:
        node = service.get_node(node_id)
        return NodeResponse(
            id=str(node.id),
            title=node.title,
            node_type=node.node_type.value,
            branch=node.branch,
            content=node.content,
            summary=node.summary,
            tags=list(node.tags),
            parent_id=str(node.parent_id) if node.parent_id else None,
            related_nodes=[str(n) for n in node.related_nodes],
            metadata=node.metadata,
            version=node.version,
            created_at=node.created_at.isoformat(),
            updated_at=node.updated_at.isoformat(),
        )
    except NodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(request: CreateNodeRequest) -> NodeResponse:
    """Create a new wiki node."""
    service = get_wiki_service()
    try:
        parent_uuid = UUID(request.parent_id) if request.parent_id else None
        node = service.create_node(
            title=request.title,
            content=request.content,
            branch=request.branch,
            node_type=request.node_type,
            parent_id=parent_uuid,
            summary=request.summary,
            tags=frozenset(request.tags),
            metadata=request.metadata,
        )
        return NodeResponse(
            id=str(node.id),
            title=node.title,
            node_type=node.node_type.value,
            branch=node.branch,
            content=node.content,
            summary=node.summary,
            tags=list(node.tags),
            parent_id=str(node.parent_id) if node.parent_id else None,
            related_nodes=[str(n) for n in node.related_nodes],
            metadata=node.metadata,
            version=node.version,
            created_at=node.created_at.isoformat(),
            updated_at=node.updated_at.isoformat(),
        )
    except DuplicateNodeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/nodes/{node_id}", response_model=NodeResponse)
async def update_node(node_id: str, request: UpdateNodeRequest) -> NodeResponse:
    """Update an existing wiki node."""
    service = get_wiki_service()
    try:
        node = service.update_node(
            node_id=node_id,
            title=request.title,
            content=request.content,
            summary=request.summary,
            tags=frozenset(request.tags) if request.tags is not None else None,
            metadata=request.metadata,
        )
        return NodeResponse(
            id=str(node.id),
            title=node.title,
            node_type=node.node_type.value,
            branch=node.branch,
            content=node.content,
            summary=node.summary,
            tags=list(node.tags),
            parent_id=str(node.parent_id) if node.parent_id else None,
            related_nodes=[str(n) for n in node.related_nodes],
            metadata=node.metadata,
            version=node.version,
            created_at=node.created_at.isoformat(),
            updated_at=node.updated_at.isoformat(),
        )
    except NodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(node_id: str) -> None:
    """Delete a wiki node."""
    service = get_wiki_service()
    try:
        service.delete_node(node_id)
    except NodeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidNodeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nodes/{node_id}/children", response_model=list[NodeResponse])
async def get_node_children(node_id: str) -> list[NodeResponse]:
    """Get direct children of a node."""
    service = get_wiki_service()
    children = service.get_children(node_id)
    return [
        NodeResponse(
            id=str(n.id),
            title=n.title,
            node_type=n.node_type.value,
            branch=n.branch,
            content=n.content,
            summary=n.summary,
            tags=list(n.tags),
            parent_id=str(n.parent_id) if n.parent_id else None,
            related_nodes=[str(rn) for rn in n.related_nodes],
            metadata=n.metadata,
            version=n.version,
            created_at=n.created_at.isoformat(),
            updated_at=n.updated_at.isoformat(),
        )
        for n in children
    ]


@router.get("/search", response_model=SearchResponse)
async def search_wiki(
    q: str = Query(..., min_length=1, description="Search query"),
    branch: Optional[WikiBranch] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    """Full-text search across wiki content."""
    query_service = get_query_service()
    result = query_service.search(query=q, branch=branch, limit=limit, offset=offset)
    return SearchResponse(
        query=result["query"],
        results=[SearchResult(**r) for r in result["results"]],
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )


@router.get("/related/{node_id}")
async def get_related_nodes(
    node_id: str,
    max_depth: int = Query(2, ge=1, le=5),
) -> list[dict]:
    """Get nodes related to the specified node through the knowledge graph."""
    service = get_graph_service()
    related = service.get_related_nodes(node_id, max_depth=max_depth)
    return related


@router.get("/tags")
async def list_tags() -> list[str]:
    """Get all unique tags across the wiki."""
    query_service = get_query_service()
    return query_service.get_all_tags()


@router.get("/stats")
async def get_wiki_stats() -> dict:
    """Get wiki statistics."""
    query_service = get_query_service()
    search_index = SearchIndex()

    counts = query_service.get_node_count_by_branch()
    recent = query_service.get_recent_nodes(limit=5)
    index_stats = search_index.get_stats()

    return {
        "nodes_by_branch": counts,
        "total_nodes": sum(counts.values()),
        "recent_nodes": recent,
        "index_stats": index_stats,
    }
