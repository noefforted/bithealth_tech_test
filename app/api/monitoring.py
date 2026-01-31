from fastapi import APIRouter, Depends
from app.core.deps import get_repo

router = APIRouter(tags=["System"])

@router.get("/status")
async def status(repo=Depends(get_repo)):
    return {
        "status": "healthy",
        "qdrant_online": repo.is_active
    }