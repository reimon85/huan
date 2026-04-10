"""Markdown file-based storage implementation for wiki nodes."""

import re
from pathlib import Path
from typing import Optional
from uuid import UUID

from trading_companion.core.config import Settings, get_settings
from trading_companion.core.exceptions import StorageError, NodeNotFoundError
from trading_companion.wiki.models import WikiNode, WikiBranch, NodeType
from trading_companion.wiki.repository import WikiRepository


class MarkdownStore(WikiRepository):
    """
    Markdown file-based storage implementation.

    Structure:
        content/
            trading/
                fundamentos.md
                analisis_tecnico.md
                ...
            trading_systems/
                price_action.md
                ...
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.content_path = self.settings.wiki_content_path
        self._ensure_content_dir()

    def _ensure_content_dir(self) -> None:
        """Ensure content directory exists."""
        if not self.content_path.exists():
            self.content_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, node: WikiNode) -> Path:
        """Get the file path for a node based on its branch and title."""
        if not node.branch:
            raise StorageError("Node must have a branch to determine file path")

        branch_dir = self.content_path / node.branch
        branch_dir.mkdir(parents=True, exist_ok=True)

        # Convert title to filename-safe string
        safe_title = re.sub(r"[^\w\s-]", "", node.title.lower())
        safe_title = re.sub(r"[\s]+", "_", safe_title)
        filename = f"{safe_title}.md"

        return branch_dir / filename

    def _parse_markdown_file(self, file_path: Path) -> Optional[WikiNode]:
        """Parse a markdown file into a WikiNode."""
        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise StorageError(f"Failed to read file {file_path}: {e}")

        # Extract frontmatter if present
        frontmatter = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text, body = parts[1], parts[2]
                for line in fm_text.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()

        # Extract title from first H1 or filename
        title = frontmatter.get("title", "")
        if not title and body.strip():
            h1_match = re.match(r"^#\s+(.+)$", body.strip(), re.MULTILINE)
            if h1_match:
                title = h1_match.group(1)
            else:
                title = file_path.stem.replace("_", " ").title()

        # Determine branch from parent directory
        branch = file_path.parent.name
        if branch == self.content_path.name:
            branch = file_path.parent.parent.name

        # Parse node type
        node_type_str = frontmatter.get("type", "article")
        try:
            node_type = NodeType(node_type_str)
        except ValueError:
            node_type = NodeType.ARTICLE

        # Parse tags
        tags_str = frontmatter.get("tags", "")
        tags = frozenset(t.strip() for t in tags_str.split(",") if t.strip())

        # Generate summary from first paragraph
        summary = ""
        lines = body.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                summary = line[:200]
                break

        return WikiNode(
            title=title,
            node_type=node_type,
            branch=branch,
            content=body.strip(),
            summary=summary,
            tags=tags,
        )

    def _serialize_node_to_markdown(self, node: WikiNode) -> str:
        """Serialize a WikiNode to markdown with frontmatter."""
        lines = ["---"]
        lines.append(f"title: {node.title}")
        lines.append(f"type: {node.node_type.value}")
        if node.branch:
            lines.append(f"branch: {node.branch}")
        if node.tags:
            lines.append(f"tags: {', '.join(node.tags)}")
        if node.summary:
            lines.append(f"summary: {node.summary}")
        lines.append("---")
        lines.append("")
        lines.append(f"# {node.title}")
        lines.append("")
        lines.append(node.content)

        return "\n".join(lines)

    def get_by_id(self, node_id: str) -> Optional[WikiNode]:
        """Retrieve a node by its UUID."""
        # In markdown store, we search by title since UUID isn't in filename
        # This is a limitation of the markdown store - consider adding ID to frontmatter
        for file_path in self._iter_markdown_files():
            node = self._parse_markdown_file(file_path)
            if node and str(node.id) == node_id:
                return node
        return None

    def save(self, node: WikiNode) -> WikiNode:
        """Save or update a node to a markdown file."""
        file_path = self._get_file_path(node)
        try:
            content = self._serialize_node_to_markdown(node)
            file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise StorageError(f"Failed to save node to {file_path}: {e}")
        return node

    def delete(self, node_id: str) -> bool:
        """Delete a node's markdown file."""
        node = self.get_by_id(node_id)
        if not node:
            return False

        file_path = self._get_file_path(node)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_by_branch(self, branch: WikiBranch) -> list[WikiNode]:
        """Get all nodes in a specific branch."""
        branch_dir = self.content_path / branch.value
        if not branch_dir.exists():
            return []

        nodes = []
        for file_path in branch_dir.glob("*.md"):
            node = self._parse_markdown_file(file_path)
            if node:
                nodes.append(node)
        return nodes

    def get_children(self, parent_id: str) -> list[WikiNode]:
        """Get all direct children of a node."""
        # In flat markdown store, children are determined by parent_id field
        # which requires parsing all nodes - not efficient but functional
        all_nodes = self._get_all_nodes()
        parent = self.get_by_id(parent_id)
        if not parent:
            return []

        return [n for n in all_nodes if n.parent_id == parent.id]

    def get_root_nodes(self) -> list[WikiNode]:
        """Get all root nodes (one per branch)."""
        return [n for n in self._get_all_nodes() if n.parent_id is None]

    def exists(self, node_id: str) -> bool:
        """Check if a node exists."""
        return self.get_by_id(node_id) is not None

    def exists_by_title(self, title: str, branch: WikiBranch) -> bool:
        """Check if a node with given title exists in branch."""
        branch_nodes = self.get_by_branch(branch)
        return any(n.title.lower() == title.lower() for n in branch_nodes)

    def _iter_markdown_files(self) -> list[Path]:
        """Iterate over all markdown files in content directory."""
        files = []
        if self.content_path.exists():
            for ext in ["*.md", "*.markdown"]:
                files.extend(self.content_path.rglob(ext))
        return files

    def _get_all_nodes(self) -> list[WikiNode]:
        """Get all nodes from all markdown files."""
        nodes = []
        for file_path in self._iter_markdown_files():
            node = self._parse_markdown_file(file_path)
            if node:
                nodes.append(node)
        return nodes
