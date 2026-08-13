from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api import router
from app.core.config import settings

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True, parents=True)

app = FastAPI(
    title="Weldtrack",
    root_path="/api",
    docs_url=None if settings.is_prod else "/docs",
    redoc_url=None if settings.is_prod else "/redoc",
    openapi_url=None if settings.is_prod else "/openapi.json",
)

# Mount static files for both /static and /api/static paths
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/api/static", StaticFiles(directory=str(STATIC_DIR)), name="api_static")

limiter = Limiter(key_func=get_remote_address, default_limits=["50/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes with /api prefix and without prefix to support both dev and proxy environments
app.include_router(router, prefix="/api")
app.include_router(router)


@app.get("/")
def root():
    return {"name": "weldtrack", "status": "online"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_prod,
    )
