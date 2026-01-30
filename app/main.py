from fastapi import FastAPI, Depends, HTTPException
from .repositories.vector_store import DocumentRepository
from .services.embedding import EmbeddingService # Assume simple class for fake_embed
from .services.rag_service import RAGService
from .models.schemas import QuestionRequest, DocumentRequest
from app.core.config import settings
import logging

app = FastAPI(title=settings.PROJECT_TITLE)

# Mengatur konfigurasi logging secara global
logging.basicConfig(
    level=settings.LOG_LEVEL, # <-- Di sini LOG_LEVEL dari .env terpakai
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Aplikasi {settings.PROJECT_TITLE} dimulai dengan Log Level: {settings.LOG_LEVEL}")
    
# Dependency Injection Containers
# In real-world, use a library like 'punq' or FastAPI Depends
repo = DocumentRepository(
    url=settings.QDRANT_URL, 
    collection_name=settings.COLLECTION_NAME,
    vector_size=settings.EMBEDDING_DIMENSION  # <-- Oper nilai dari config ke repo
)
embed_service = EmbeddingService()
rag_service = RAGService(repo, embed_service)

@app.post("/ask")
async def ask(req: QuestionRequest):
    try:
        result = rag_service.execute(req.question)
        return {"answer": result["answer"], "context": result.get("context", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_doc(req: DocumentRequest):
    try:
        # 1. Dapatkan vektor dari teks
        vector = embed_service.get_embedding(req.text)
        
        # 2. Panggil repo dengan menyebutkan nama parameternya agar tidak tertukar
        # Kita tidak perlu lagi kirim doc_id manual karena repo sudah buat UUID otomatis
        repo.add(vector=vector, text=req.text)
        
        return {"status": "success", "message": "Document added to Qdrant/Memory"}
    except Exception as e:
        logger.error(f"Error pada endpoint /add: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status():
    return {"qdrant_online": repo.is_active}