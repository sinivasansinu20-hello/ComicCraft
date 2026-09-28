import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("comiccraft")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown tasks."""
    logger.info("Starting ComicCraft application server...")
    logger.info("Static directory: %s", settings.static_dir)
    logger.info("Panels directory: %s", settings.panels_dir)
    logger.info("Exports directory: %s", settings.exports_dir)
    yield
    logger.info("Shutting down ComicCraft application...")


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Multi-agent comic generation platform leveraging Gemini Flash, Gemini Pro, and Stable Diffusion.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static asset directory
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Register routes
app.include_router(router)


@app.get("/health", tags=["System"])
async def health_check():
    """System health check and diagnostic status."""
    return {
        "status": "healthy",
        "app": "ComicCraft",
        "version": "1.0.0",
        "gemini_configured": bool(settings.gemini_api_key),
        "hf_configured": bool(settings.hf_api_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
