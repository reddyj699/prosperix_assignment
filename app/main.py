from fastapi import FastAPI

from app.api import routes
from app.core.background import start_background_tasks
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(start_background_tasks())
    yield
    # Shutdown
    # task.cancel() # Optional: cancel background task on shutdown

app = FastAPI(
    title="Product Availability & Pricing Normalization Service",
    description="Normalizes product data from multiple vendors with rate limiting and caching.",
    version="1.0.1",
    lifespan=lifespan
)

app.include_router(routes.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
