"""Hermes Agent plugin entry point for Trading Companion.

Este módulo expone la función ``register`` que Hermes llama al cargar el plugin
vía entry points (``hermes_agent.plugins``) o desde el directorio de plugins.
"""

from trading_companion.tools import market_data, wiki_context  # noqa: F401


def register(ctx) -> None:
    """Register Trading Companion tools and hooks.

    Este entry point se usa tanto por el sistema de plugins de Hermes
    (``~/.hermes/plugins/``) como por el entry point de pip.
    """
    # Las tools se auto-registran al importar los módulos arriba.
    # Aquí podemos registrar hooks adicionales si es necesario.
    pass
