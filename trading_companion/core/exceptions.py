"""Custom exceptions for the wiki module."""


class WikiException(Exception):
    """Base exception for all wiki-related errors."""

    pass


class NodeNotFoundError(WikiException):
    """Raised when a requested wiki node does not exist."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        super().__init__(f"Wiki node not found: {node_id}")


class DuplicateNodeError(WikiException):
    """Raised when attempting to create a node that already exists."""

    def __init__(self, title: str, branch: str) -> None:
        self.title = title
        self.branch = branch
        super().__init__(f"Node already exists: {title} in {branch}")


class InvalidNodeError(WikiException):
    """Raised when node data is invalid or incomplete."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid node: {message}")


class SearchError(WikiException):
    """Raised when search operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Search error: {message}")


class StorageError(WikiException):
    """Raised when storage operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Storage error: {message}")
