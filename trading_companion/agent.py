#!/usr/bin/env python3
"""
Trading Agent — Interface to Claude for trading companion.

Usage:
    python -m trading_companion.agent "What should I watch today?"
    python -m trading_companion.agent --mode analysis "EURUSD setup validation"
    python -m trading_companion.agent --mode debrief
"""

import os
import sys
import json
import argparse
import httpx
from datetime import datetime
from pathlib import Path

# Configuration
N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5678")


def fetch_webhook(endpoint: str) -> str:
    """Fetch data from n8n webhook."""
    url = f"{WEBHOOK_URL}{endpoint}"
    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"[Error fetching {endpoint}: {e}]"


def fetch_all_context() -> dict:
    """Fetch all available context from n8n webhooks."""
    print("📡 Fetching context from n8n...")

    # Parallel fetch of all data
    with httpx.Client(timeout=30) as client:
        endpoints = {
            "briefing": "/webhook/briefing-today",
            "prices": "/webhook/prices",
            "prices_alerts": "/webhook/prices-alerts",
            "sentiment": "/webhook/sentiment",
            "news_latest": "/webhook/news-latest",
            "news_urgent": "/webhook/news-urgent",
            "calendar": "/webhook/calendar-today",
            "cot": "/webhook/cot-latest",
            "crypto_snapshot": "/webhook/crypto-snapshot",
            "crypto_regime": "/webhook/crypto-regime",
        }

        results = {}
        for name, endpoint in endpoints.items():
            try:
                resp = client.get(f"{WEBHOOK_URL}{endpoint}")
                if resp.status_code == 200:
                    results[name] = resp.text
                else:
                    results[name] = f"[{resp.status_code}]"
            except Exception as e:
                results[name] = f"[Error: {e}]"

    return results


def build_system_prompt() -> str:
    """Build the system prompt from the wiki."""
    # Read system prompt from wiki
    wiki_path = Path(__file__).parent / "wiki" / "content" / "seeds" / "trading_systems" / "system_prompt_maestro.md"

    if wiki_path.exists():
        with open(wiki_path) as f:
            system_prompt = f.read()
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    return system_prompt


def build_user_context(context_data: dict, mode: str, user_message: str) -> str:
    """Build the user context with fetched data."""

    context = f"""=== CONTEXTO DE MERCADO — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===

"""

    # Add available context
    if context_data.get("briefing"):
        context += f"=== BRIEFING DEL DÍA ===\n{context_data['briefing']}\n\n"

    if context_data.get("prices"):
        context += f"=== PRECIOS ===\n{context_data['prices']}\n\n"

    if context_data.get("prices_alerts") and "Error" not in context_data.get("prices_alerts", ""):
        context += f"=== ALERTAS DE PRECIO ===\n{context_data['prices_alerts']}\n\n"

    if context_data.get("sentiment"):
        context += f"=== SENTIMENT ===\n{context_data['sentiment']}\n\n"

    if context_data.get("news_urgent") and "Error" not in context_data.get("news_urgent", ""):
        context += f"=== NOTICIAS URGENTES ===\n{context_data['news_urgent']}\n\n"

    if context_data.get("calendar"):
        context += f"=== CALENDARIO ECONÓMICO ===\n{context_data['calendar']}\n\n"

    if context_data.get("cot") and "Error" not in context_data.get("cot", ""):
        context += f"=== COT ===\n{context_data['cot']}\n\n"

    if context_data.get("crypto_snapshot"):
        context += f"=== CRYPTO ===\n{context_data['crypto_snapshot']}\n\n"

    # Mode-specific context
    if mode == "analysis":
        context += f"""=== ANÁLISIS DE EVENTO MACRO/GEOPOLÍTICO ===
El trader reporta: {user_message}

Analiza el evento descrito usando el contexto de mercado actual.
"""
    elif mode == "setup":
        context += f"""=== VALIDACIÓN DE SETUP ===
El trader describe: {user_message}

Valida el setup propuesto con los datos actuales.
"""
    elif mode == "debrief":
        context += f"""=== DEBRIEF POST-SESIÓN ===
{user_message}

Analiza la sesión usando los datos disponibles y extrae lecciones.
"""
    else:
        context += f"""=== CONSULTA DEL TRADER ===
{user_message}
"""

    return context


def call_claude(system_prompt: str, user_message: str) -> str:
    """Make API call to Claude."""
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not set"

    try:
        import anthropic
        client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            base_url=ANTHROPIC_BASE_URL
        )

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )

        # Handle response - can be text or thinking blocks
        if hasattr(response.content[0], 'text'):
            return response.content[0].text
        elif hasattr(response.content[0], 'thinking'):
            # Return thinking + extracted text
            thinking = response.content[0].thinking[:500] if response.content[0].thinking else ""
            # Try to find a text block
            for block in response.content:
                if hasattr(block, 'text') and block.text:
                    return f"[Thinking: {thinking}...]\n\n{block.text}"
            return f"[Thinking: {thinking}...]"
        else:
            return str(response.content[0])
    except ImportError:
        return "Error: anthropic package not installed. Run: pip install anthropic"
    except Exception as e:
        return f"Error calling Claude: {e}"


DEFAULT_SYSTEM_PROMPT = """Eres un analista de mercados financieros senior y copiloto de trading discrecional.
Tu función es asistir a un trader discrecional con experiencia que opera Forex, Futuros, Crypto y Materias Primas.

Tienes acceso en tiempo real a:
- Precios de mercado (Forex, índices, crypto)
- Calendario económico del día
- Sentiment aggregate (Fear & Greed)
- Posicionamiento COT semanal
- News urgentes
- Snapshot de crypto (funding, OI, dominance)

Respondes de forma:
- Directa y técnica
- Enfocada en probabilidades y escenarios
- Sin predictions ciertas
- Con honestidad sobre incertidumbre

Cuando el trader pregunta, struktura tu respuesta:
1. CONTEXTO (qué veo)
2. ANÁLISIS (por qué)
3. ESCENARIOS (qué puede pasar)
4. CONDICIÓN DE INVALIDACIÓN (cuándo estarías equivocado)
"""


def main():
    parser = argparse.ArgumentParser(description="Trading Agent - Claude Interface")
    parser.add_argument("message", nargs="?", help="Message to send to the agent")
    parser.add_argument("--mode", choices=["analysis", "setup", "debrief", "chat"],
                        default="chat", help="Mode of interaction")
    parser.add_argument("--no-fetch", action="store_true", help="Skip fetching n8n context")
    parser.add_argument("--system", action="store_true", help="Show system prompt and exit")

    args = parser.parse_args()

    # Show system prompt
    if args.system:
        print(build_system_prompt())
        return

    if not args.message:
        print("Trading Agent CLI")
        print("=" * 50)
        print("Usage:")
        print("  python -m trading_companion.agent 'Qué vigilar hoy?'")
        print("  python -m trading_companion.agent --mode analysis 'Evento: Fed speech'")
        print("  python -m trading_companion.agent --mode debrief 'Sesión: +2R hoy'")
        print("  python -m trading_companion.agent --system (show prompt)")
        return

    # Build prompts
    system_prompt = build_system_prompt()

    if args.no_fetch:
        user_context = args.message
    else:
        print("📡 Fetching market context...")
        context_data = fetch_all_context()
        user_context = build_user_context(context_data, args.mode, args.message)

    # Call Claude
    print("\n🤖 Claude responding...")
    response = call_claude(system_prompt, user_context)

    print("\n" + "=" * 50)
    print(response)


if __name__ == "__main__":
    main()
