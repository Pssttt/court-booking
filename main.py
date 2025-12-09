"""
Main FastAPI Application
Application initialization and startup
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from config.settings import COURTS, DEFAULT_SUBMIT_TIME, SERVER
from app.routes import router
from app.templates import get_booking_form_html

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the booking form"""
    return get_booking_form_html(COURTS, DEFAULT_SUBMIT_TIME)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=SERVER["host"], port=SERVER["port"], reload=SERVER["debug"]
    )
