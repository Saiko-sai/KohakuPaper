"""
FastAPI application setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import papers, statistics, data, sync


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="KohakuPaper API",
        description="API for paper data analysis and visualization",
        version="0.4.0",
    )

    # CORS middleware for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5175",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
    app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
    app.include_router(data.router, prefix="/api/data", tags=["data"])
    app.include_router(sync.router, prefix="/api/sync", tags=["sync"])

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
