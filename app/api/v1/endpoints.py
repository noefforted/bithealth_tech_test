from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import QuestionRequest, DocumentRequest
from app.core.deps import get_rag_service, get_embed_service, get_repo
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ask")
async def ask(req: QuestionRequest, rag=Depends(get_rag_service)):
    try:
        result = rag.execute(req.question)
        return {"answer": result["answer"], "context": result.get("context", [])}
    except Exception as e:
        logger.error(f"Error pada /ask: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/add")
async def add_doc(req: DocumentRequest, embed=Depends(get_embed_service), repo=Depends(get_repo)):
    try:
        vector = embed.get_embedding(req.text)
        repo.add(vector=vector, text=req.text)
        return {"status": "success", "message": "Document added"}
    except Exception as e:
        logger.error(f"Error pada /add: {e}")
        raise HTTPException(status_code=500, detail=str(e))