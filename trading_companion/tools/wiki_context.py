"""Trading Companion — Wiki Context Tool.

Permite al agente consultar la base de conocimiento interna (wiki) de trading
para enriquecer sus respuestas con conocimiento estructurado.
"""

import logging
from pathlib import Path
from typing import Any

from tools.registry import registry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WIKI_PATH = Path(__file__).parent.parent / "wiki" / "content" / "seeds"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _search_wiki(query: str) -> str:
    """Simple keyword search over wiki markdown files."""
    if not WIKI_PATH.exists():
        return "[Wiki no encontrada]"

    matches = []
    query_lower = query.lower()

    for md_file in WIKI_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if query_lower in content.lower():
                # Extract title from first heading
                title = md_file.stem.replace("_", " ").title()
                for line in content.splitlines()[:10]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

                # Extract a snippet around the match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 200)
                end = min(len(content), idx + 400)
                snippet = content[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                matches.append(f"## {title}\n{snippet}\n")
        except Exception as e:
            logger.debug("Error reading %s: %s", md_file, e)

    if not matches:
        return f"No se encontró contenido en la wiki para: '{query}'"

    return "\n".join(matches[:5])  # limit to top 5 matches


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

def _handle_fetch_wiki_context(args: dict, **kwargs: Any) -> str:
    """Fetch relevant content from the internal trading wiki."""
    query = args.get("query", "")
    if not query:
        return "Se requiere un término de búsqueda (query)."

    return _search_wiki(query)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_FETCH_WIKI_CONTEXT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "fetch_wiki_context",
        "description": (
            "Busca información relevante en la base de conocimiento interna (wiki) "
            "de trading. Usar cuando se necesite conocimiento específico sobre "
            "estrategias, gestión de riesgo, indicadores, psicología, etc."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término o concepto a buscar en la wiki (ej: 'RSI', 'order block', 'gestión de riesgo')",
                },
            },
            "required": ["query"],
        },
    },
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="fetch_wiki_context",
    toolset="trading",
    schema=_FETCH_WIKI_CONTEXT_SCHEMA,
    handler=_handle_fetch_wiki_context,
    check_fn=lambda: WIKI_PATH.exists(),
    emoji="📚",
    max_result_size_chars=100_000,
)
