from fastapi import FastAPI
from server.routes import hana_routes, vera_routes, mira_routes, shared_routes
from contextlib import asynccontextmanager
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ startup
    logger.info("🚀 API Server starting...")
    yield
    # ✅ shutdown
    logger.info("🛑 API Server shutting down...")

app = FastAPI(lifespan=lifespan)

# รวมทุก route ที่แยก module ไว้
app.include_router(shared_routes.router, prefix="/api/shared", tags=["Shared"])
app.include_router(hana_routes.router, prefix="/api/hana", tags=["HANA"])
app.include_router(vera_routes.router, prefix="/api/vera", tags=["VERA"])
app.include_router(mira_routes.router, prefix="/api/mira", tags=["MIRA"])