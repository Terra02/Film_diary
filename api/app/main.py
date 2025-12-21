from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from app.routers import (
    users_router, content_router, view_history_router,
    watchlist_router, analytics_router
)

from app.routers.bot_content import router as bot_content_router
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movie Tracker API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(view_history_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(bot_content_router, prefix="/api/v1")


@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединений при выключении"""
    from app.services.worker_adapter import worker_adapter
    await worker_adapter.close()
    logger.info("Worker adapter closed")