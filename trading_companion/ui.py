#!/usr/bin/env python3
"""
Trading Agent Web UI

Simple web interface to chat with the trading agent.

Run:
    python -m trading_companion.ui
    Then open: http://localhost:8001
"""

import os
import sys
import json
import httpx
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates

# Load environment
def load_env():
    env_file = Path(__file__).parent.parent / "trading-agent" / ".env.local"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ.setdefault(key, value)

load_env()

# Config
N8N_URL = os.getenv("WEBHOOK_URL", "http://localhost:5678")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.minimax.io/anthropic")
ANTHROPIC_MODEL = os.getenv("LLM_MODEL", "MiniMax-M2.7")

app = FastAPI(title="Trading Agent UI")

# Simple in-memory chat history
chat_history: list[dict] = []


def fetch_webhook(endpoint: str) -> str:
    """Fetch data from n8n webhook."""
    try:
        response = httpx.get(f"{N8N_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return ""


def fetch_all_context() -> dict:
    """Fetch all context from n8n."""
    with httpx.Client(timeout=15) as client:
        endpoints = {
            "briefing": "/webhook/briefing-today",
            "prices": "/webhook/prices",
            "sentiment": "/webhook/sentiment",
            "news_urgent": "/webhook/news-urgent",
            "calendar": "/webhook/calendar-today",
            "crypto_snapshot": "/webhook/crypto-snapshot",
        }
        results = {}
        for name, endpoint in endpoints.items():
            try:
                resp = client.get(f"{N8N_URL}{endpoint}")
                results[name] = resp.text if resp.status_code == 200 else ""
            except:
                results[name] = ""
        return results


def build_context(context_data: dict, user_message: str) -> str:
    """Build context string from n8n data."""
    ctx = f"=== CONTEXTO — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n\n"

    if context_data.get("briefing"):
        ctx += f"=== BRIEFING ===\n{context_data['briefing']}\n\n"
    if context_data.get("prices"):
        ctx += f"=== PRECIOS ===\n{context_data['prices']}\n\n"
    if context_data.get("sentiment"):
        ctx += f"=== SENTIMENT ===\n{context_data['sentiment']}\n\n"
    if context_data.get("news_urgent"):
        ctx += f"=== NOTICIAS URGENTES ===\n{context_data['news_urgent']}\n\n"
    if context_data.get("calendar"):
        ctx += f"=== CALENDARIO ===\n{context_data['calendar']}\n\n"
    if context_data.get("crypto_snapshot"):
        ctx += f"=== CRYPTO ===\n{context_data['crypto_snapshot']}\n\n"

    ctx += f"=== CONSULTA ===\n{user_message}"
    return ctx


SYSTEM_PROMPT = """Eres un analista de mercados financieros senior y copiloto de trading discrecional. Tu función es asistir a un trader discrecional con experiencia que opera Forex (majors y crosses), Futuros (ES, NQ, CL, GC y otros), criptomonedas y materias primas, con un estilo mixto: intradiario cuando el contexto lo justifica, swing cuando la estructura lo permite.

## Tu identidad como especialista

Tienes profundo conocimiento en estas áreas y las integras de forma simultánea al analizar cualquier situación de mercado:

### Macro y geopolítica aplicada a precio

Comprendes cómo los eventos geopolíticos, conflictos armados, sanciones, decisiones de la OPEP, tensiones entre grandes potencias y shocks externos impactan los flujos de capital y el precio de los activos.

### Análisis intermercado

Lee los mercados como un sistema interconectado — DXY ↔ Materias primas, Bonos ↔ Renta variable, Oro ↔ Tipos reales, VIX ↔ ES intradiario, Bitcoin ↔ Risk appetite.

### Comportamiento de precio y microestructura

Entiendes gaps técnicos vs fundamentales, aperturas de mercado, liquidez en zonas institucionales, formación de rangos, distribución vs acumulación.

### Psicología colectiva y sentiment

Sabes leer el posicionamiento del mercado: Reportes COT, indicadores de sentiment, narrativa dominante, consenso excesivo.

## Cómo respondes

- **Estructuras tu razonamiento**: qué ves → por qué → escenarios → condición de invalidación
- **Nunca das señales de entrada directas**. Eres un copiloto, no un gestor de órdenes.
- **Cuando el contexto es incierto, lo dices**.
- **Hablas como un colega experimentado**. Directo, técnico, sin jerga innecesaria.

## Lo que NO haces

- ❌ Dar consejos de inversión en sentido legal
- ❌ Predecir precios con certeza — siempre probabilidades y escenarios
- ❌ Validar operaciones sin lógica por presión"""


def ask_claude(message: str, context: str = "") -> str:
    """Call Claude API."""
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY not configured"

    try:
        client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            base_url=ANTHROPIC_BASE_URL
        )

        full_prompt = context + f"\n\n{message}" if context else message

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": full_prompt}]
        )

        # Handle response - ignore thinking blocks
        for block in response.content:
            if hasattr(block, 'text') and block.text:
                return block.text

        return str(response.content[0])

    except Exception as e:
        return f"Error: {str(e)}"


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: #1a1a24;
            padding: 15px 20px;
            border-bottom: 1px solid #2a2a3a;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        header h1 { font-size: 1.2rem; color: #7c3aed; }
        header .status {
            font-size: 0.8rem;
            color: #888;
        }
        .status-dot {
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #4ade80;
            margin-right: 5px;
        }
        .status-dot.error { background: #f87171; }
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
            font-size: 0.95rem;
        }
        .message.user {
            background: #7c3aed;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .message.agent {
            background: #1a1a24;
            border: 1px solid #2a2a3a;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }
        .message.error {
            background: #7f1d1d;
            border: 1px solid #991b1b;
            color: #fecaca;
        }
        .message.context {
            background: #1e293b;
            border: 1px solid #334155;
            font-size: 0.85rem;
            max-width: 95%;
        }
        .typing {
            align-self: flex-start;
            padding: 12px 16px;
            background: #1a1a24;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            color: #888;
            font-style: italic;
        }
        #input-area {
            background: #1a1a24;
            padding: 15px 20px;
            border-top: 1px solid #2a2a3a;
        }
        #input-area form {
            display: flex;
            gap: 10px;
            max-width: 900px;
            margin: 0 auto;
        }
        #message {
            flex: 1;
            padding: 12px 16px;
            background: #0a0a0f;
            border: 1px solid #2a2a3a;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
        }
        #message:focus { outline: none; border-color: #7c3aed; }
        button {
            padding: 12px 24px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover { background: #6d28d9; }
        button:disabled { background: #4a4a5a; cursor: not-allowed; }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            justify-content: center;
        }
        .controls button {
            padding: 8px 16px;
            font-size: 0.85rem;
            background: #2a2a3a;
        }
        .controls button:hover { background: #3a3a4a; }
        .controls button.active { background: #7c3aed; }
        .timestamp {
            font-size: 0.7rem;
            color: #666;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <header>
        <h1>📈 Trading Agent</h1>
        <div class="status">
            <span class="status-dot" id="n8n-status"></span>
            <span id="n8n-text">Checking n8n...</span>
        </div>
    </header>

    <div class="controls">
        <button onclick="sendMessage('Qué vigilar hoy?', 'quick')" title="Get daily briefing">📋 Briefing</button>
        <button onclick="sendMessage('Analiza el sentiment actual', 'quick')" title="Analyze sentiment">📊 Sentiment</button>
        <button onclick="sendMessage('Qué eventos macro hay hoy?', 'quick')" title="Check macro events">📅 Calendario</button>
        <button onclick="sendMessage('Estado del mercado crypto', 'quick')" title="Crypto market">₿ Crypto</button>
        <button onclick="clearChat()">🗑️ Clear</button>
    </div>

    <div id="chat"></div>

    <div id="input-area">
        <form onsubmit="sendMessage(this.message.value, 'chat'); return false;">
            <input type="text" id="message" placeholder="Ask about the markets..." autocomplete="off">
            <button type="submit" id="send-btn">Send</button>
        </form>
    </div>

    <script>
        let isThinking = false;

        async function checkN8n() {
            try {
                const resp = await fetch('/api/n8n-status');
                const data = await resp.json();
                document.getElementById('n8n-status').className = data.ok ? 'status-dot' : 'status-dot error';
                document.getElementById('n8n-text').textContent = data.ok ? 'n8n connected' : 'n8n offline';
            } catch {
                document.getElementById('n8n-status').className = 'status-dot error';
                document.getElementById('n8n-text').textContent = 'n8n unreachable';
            }
        }

        function addMessage(content, type, time = null) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = content;
            if (time) {
                const ts = document.createElement('div');
                ts.className = 'timestamp';
                ts.textContent = time;
                div.appendChild(ts);
            }
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            return div;
        }

        function setThinking(thinking) {
            const chat = document.getElementById('chat');
            if (thinking) {
                if (!document.getElementById('typing')) {
                    const div = document.createElement('div');
                    div.id = 'typing';
                    div.className = 'typing';
                    div.textContent = 'Thinking...';
                    chat.appendChild(div);
                }
            } else {
                const el = document.getElementById('typing');
                if (el) el.remove();
            }
            isThinking = thinking;
            document.getElementById('send-btn').disabled = thinking;
        }

        async function sendMessage(text, mode) {
            if (!text.trim() || isThinking) return;

            // Add user message
            addMessage(text, 'user', new Date().toLocaleTimeString());

            // Get context if chat mode
            let context = '';
            if (mode === 'chat') {
                setThinking(true);
                try {
                    const resp = await fetch('/api/context');
                    context = await resp.text();
                    addMessage('Fetching market context...', 'context');
                } catch (e) {
                    console.error('Context fetch error:', e);
                }
            }

            setThinking(true);

            try {
                const resp = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text, context: context})
                });
                const data = await resp.json();
                addMessage(data.response, 'agent', new Date().toLocaleTimeString());
            } catch (e) {
                addMessage('Error: Could not reach the agent', 'error');
            }

            setThinking(false);
        }

        function clearChat() {
            document.getElementById('chat').innerHTML = '';
        }

        // Check n8n status on load
        checkN8n();
        setInterval(checkN8n, 30000);

        // Focus input
        document.getElementById('message').focus();
    </script>
</body>
</html>
"""


@app.get("/")
async def root():
    return HTMLResponse(HTML_PAGE)


@app.get("/api/n8n-status")
async def n8n_status():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{N8N_URL}/webhook/briefing-today")
            return {"ok": resp.status_code == 200}
    except:
        return {"ok": False}


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    context = body.get("context", "")

    response = ask_claude(message, context)
    return {"response": response}


@app.get("/api/context")
async def get_context():
    """Fetch all context from n8n."""
    data = fetch_all_context()
    return build_context(data, "")


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Trading Agent UI")
    print("=" * 50)
    print("Open: http://localhost:8001")
    print()
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8001)
