"""WikiBranch enumeration - the 6 main knowledge branches."""

from enum import Enum


class WikiBranch(Enum):
    """The 6 main wiki branches."""

    TRADING = "trading"
    TRADING_SYSTEMS = "trading_systems"
    DATA_ANALYSIS = "data_analysis"
    TRADING_BOTS = "trading_bots"
    PSICOLOGIA_TRADING = "psicologia_trading"
    REGULACION = "regulacion"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        return {
            "trading": "Trading",
            "trading_systems": "Trading Systems",
            "data_analysis": "Data Analysis",
            "trading_bots": "Trading Bots",
            "psicologia_trading": "Psicología Trading",
            "regulacion": "Regulación",
        }[self.value]

    @property
    def subtopics(self) -> list[str]:
        """Standard subtopics for each branch."""
        return SUBTOPICS.get(self.value, [])


# Standard subtopic structure across branches
SUBTOPICS: dict[str, list[str]] = {
    "trading": [
        "Fundamentos",
        "Análisis Técnico",
        "Análisis Fundamental",
        "Gestión de Riesgo",
        "Estrategias",
        "Mercados",
    ],
    "trading_systems": [
        "Diseño de Sistemas",
        "Backtesting",
        "Optimización",
        "Ejecución",
        "Monitoreo",
        "Documentación",
    ],
    "data_analysis": [
        "Fuentes de Datos",
        "Limpieza de Datos",
        "Indicadores",
        "Estadística",
        "Visualización",
        "Machine Learning",
    ],
    "trading_bots": [
        "Arquitectura",
        "APIs de Broker",
        "Estrategias Bot",
        "Gestión de Órdenes",
        "Seguridad",
        "Monitoreo",
    ],
    "psicologia_trading": [
        "Control Emocional",
        "Sesgos Cognitivos",
        "Disciplina",
        "Plan de Trading",
        "Journaling",
        "Mindset",
    ],
    "regulacion": [
        "Marco Legal",
        "Compliance",
        "Taxonomía",
        "Reportes",
        "Protección de Capital",
        "Jurisdicción",
    ],
}
