"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import check_db_connection
from app.routers import documents as documents_router

app = FastAPI(
    title="Document Management API",
    description=(
        "Fullstack CRUD untuk interkoneksi data keuangan. "
        "Chapter 5: Oracle Integration | Chapter 6: Next.js Consumer."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(documents_router.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    db_ok = check_db_connection()
    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "unreachable",
            "version": "1.0.0",
        },
    )


@app.get("/", tags=["health"])
def root():
    return {
        "message": "Document Management API",
        "docs": "/docs",
        "health": "/health",
    }
