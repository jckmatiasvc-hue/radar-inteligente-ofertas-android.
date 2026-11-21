import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = os.getenv("DB_PATH", "/tmp/radar_prices.db")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()
MIN_DROP_PERCENT = float(os.getenv("MIN_DROP_PERCENT", "15"))

app = FastAPI(title="Radar Inteligente de Ofertas API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_key TEXT NOT NULL,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                source TEXT,
                link TEXT,
                observed_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_price_key ON price_history(product_key, observed_at)")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "service": "radar-inteligente-ofertas"}

@app.get("/api/deals")
def search_deals(
    q: str = Query(..., min_length=2, max_length=120),
    limit: int = Query(20, ge=1, le=50),
):
    if not SERPAPI_KEY:
        raise HTTPException(status_code=503, detail="Servidor sem SERPAPI_KEY configurada.")
    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google_shopping", "q": q, "api_key": SERPAPI_KEY, "hl": "pt", "gl": "br"},
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao consultar o provedor de pesquisa: {exc.__class__.__name__}")

    results = []
    now = datetime.now(timezone.utc).isoformat()
    with db() as conn:
        for item in payload.get("shopping_results", [])[:limit]:
            title = (item.get("title") or "").strip()
            source = item.get("source") or ""
            link = item.get("link") or item.get("product_link") or ""
            price = item.get("extracted_price")
            if price is None:
                continue
            try:
                price = float(price)
            except (TypeError, ValueError):
                continue
            if not title or price <= 0:
                continue

            # Identificador aproximado; o histórico melhora conforme o mesmo item reaparece.
            product_key = (title.lower()[:180] + "|" + source.lower()[:80]).strip()
            previous = conn.execute(
                "SELECT MIN(price) AS lowest, COUNT(*) AS samples FROM price_history WHERE product_key=?",
                (product_key,),
            ).fetchone()
            lowest = previous["lowest"]
            samples = previous["samples"]
            drop = round((1 - price / lowest) * 100, 1) if lowest and lowest > 0 else None
            # Primeira observação cria a linha de base; não é anunciada como desconto comprovado.
            good_deal = bool(samples >= 2 and drop is not None and drop >= MIN_DROP_PERCENT)

            conn.execute(
                "INSERT INTO price_history(product_key,title,price,source,link,observed_at) VALUES(?,?,?,?,?,?)",
                (product_key, title, price, source, link, now),
            )
            results.append({
                "title": title,
                "price": price,
                "currency": "BRL",
                "source": source,
                "link": link,
                "thumbnail": item.get("thumbnail"),
                "rating": item.get("rating"),
                "reviews": item.get("reviews"),
                "previous_lowest_price": lowest,
                "drop_percent": drop,
                "samples_before": samples,
                "verified": bool(samples >= 2),
                "good_deal": good_deal,
            })

    return {
        "query": q,
        "count": len(results),
        "deals": results,
        "note": "Descontos só são sinalizados após histórico suficiente neste servidor; preço de primeira consulta é apenas referência inicial."
    }

@app.get("/api/history")
def history(q: str = Query(..., min_length=2, max_length=120)):
    with db() as conn:
        rows = conn.execute(
            "SELECT title, price, source, observed_at FROM price_history WHERE title LIKE ? ORDER BY observed_at DESC LIMIT 50",
            (f"%{q}%",),
        ).fetchall()
    return {"count": len(rows), "history": [dict(row) for row in rows]}
