"""
Main FastAPI Application
Application initialization and startup
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config.settings import SERVER
from app.routes import router
from app.storage import ensure_data_dir

TEMPLATES_DIR = Path(__file__).parent / "app" / "templates"
STATIC_DIR = Path(__file__).parent / "app" / "static"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_data_dir()
    """Handle app startup and shutdown"""
    logger.info("Court Booking WebApp started")
    yield
    logger.info("Court Booking WebApp stopped")


app = FastAPI(
    title="Court Booking WebApp",
    description="Auto-book badminton courts at scheduled times",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
async def home():
    """Serve the booking form"""
    return FileResponse(TEMPLATES_DIR / "booking.html", media_type="text/html")


@app.get("/bookings", response_class=FileResponse)
async def view_bookings():
    """Serve the bookings view page"""
    return FileResponse(TEMPLATES_DIR / "bookings.html", media_type="text/html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=SERVER["host"], port=SERVER["port"], reload=SERVER["debug"]
    )
