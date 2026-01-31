import logging
from fastapi import FastAPI
from app.configs.config import settings
from app.api.v1.endpoints import router as rag_router
from app.api.monitoring import router as monitoring_router

logging.basicConfig(level=settings.LOG_LEVEL)
app = FastAPI(title=settings.PROJECT_TITLE)

# Registrasi Router
app.include_router(monitoring_router) # Tanpa prefix agar tetap /status
app.include_router(rag_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logging.getLogger(__name__).info("🚀 Application started")