"""
KW AI Demo Chatbot — Python/FastAPI Server
==========================================
Serves AI chatbot demos for Key West local businesses.
Each business has its own knowledge base in /businesses/*.json

Run locally:
    uvicorn main:app --reload --port 3000

Deploy to Render:
    Uses render.yaml — just push to GitHub and connect.
"""

import json
import os
from pathlib import Path
from typing import AsyncGenerator

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

# ── App setup ──────────────────────────────────────────────────────────────
app = FastAPI(title="KW AI Demo Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Paths
BASE_DIR = Path(__file__).parent
BUSINESSES_DIR = BASE_DIR / "businesses"
PUBLIC_DIR = BASE_DIR / "public"

# Password — set DEMO_PASSWORD in your Render environment variables
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "keywest2026")


# ── Models ─────────────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class AuthRequest(BaseModel):
    password: str


# ── Business helpers ───────────────────────────────────────────────────────
def load_business(business_id: str) -> dict:
    """Load a business config from its JSON file."""
    filepath = BUSINESSES_DIR / f"{business_id}.json"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Business '{business_id}' not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_businesses() -> list[dict]:
    """Return all businesses as summary dicts (no system_prompt)."""
    businesses = []
    for filepath in sorted(BUSINESSES_DIR.glob("*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        businesses.append({
            "id": data["id"],
            "name": data["name"],
            "tagline": data["tagline"],
            "logo_emoji": data["logo_emoji"],
        })
    return businesses


# ── API Routes ─────────────────────────────────────────────────────────────

@app.post("/api/auth")
def authenticate(request: AuthRequest):
    """
    Check the demo password for internal access.
    Returns {"ok": true} on success, 401 on failure.
    """
    if request.password == DEMO_PASSWORD:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Incorrect password")


@app.get("/api/businesses")
def get_businesses():
    """List all available businesses."""
    return list_businesses()


@app.get("/api/business/{business_id}")
def get_business(business_id: str):
    """Get a single business config (system_prompt excluded for security)."""
    data = load_business(business_id)
    return {k: v for k, v in data.items() if k != "system_prompt"}


@app.post("/api/chat/{business_id}")
async def chat(business_id: str, request: ChatRequest):
    """
    Streaming chat endpoint.
    Returns Server-Sent Events (SSE) — each chunk is:
        data: {"text": "..."}
    Final chunk:
        data: {"done": true}
    """
    business = load_business(business_id)
    system_prompt = business.get("system_prompt", "You are a helpful assistant.")

    if not request.messages:
        raise HTTPException(status_code=400, detail="messages list cannot be empty")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def stream_response() -> AsyncGenerator[str, None]:
        try:
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text_chunk in stream.text_stream:
                    payload = json.dumps({"text": text_chunk})
                    yield f"data: {payload}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"

        except anthropic.APIError as e:
            error_payload = json.dumps({"error": f"API error: {str(e)}"})
            yield f"data: {error_payload}\n\n"
        except Exception as e:
            error_payload = json.dumps({"error": "Something went wrong. Please try again."})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Static files + SPA fallback ────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Catch-all: serve index.html for any non-API route."""
    index = PUBLIC_DIR / "index.html"
    return FileResponse(str(index))


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3000))
    print(f"🚀 KW AI Demo running on http://localhost:{port}")
    print(f"📁 Businesses: {[b['id'] for b in list_businesses()]}")
    print(f"🔐 Password protection: {'ON' if DEMO_PASSWORD else 'OFF'}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
