from .users import router as users_router
from .content import router as content_router
from .view_history import router as view_history_router
from .watchlist import router as watchlist_router
from .analytics import router as analytics_router
from .bot_content import router as bot_content_router

__all__ = [
    "users_router",
    "content_router",
    "view_history_router", 
    "watchlist_router",
    "analytics_router",
    "bot_content_router"
]