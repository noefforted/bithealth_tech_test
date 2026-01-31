from app.configs.config import settings
from app.repositories.vector_store import DocumentRepository
from app.services.embedding import EmbeddingService
from app.services.rag_service import RAGService

# Inisialisasi mesin utama (Infrastructure & Services)
repo = DocumentRepository(
    url=settings.QDRANT_URL, 
    collection_name=settings.COLLECTION_NAME,
    vector_size=settings.EMBEDDING_DIMENSION
)
embed_service = EmbeddingService()
rag_service = RAGService(repo, embed_service)

# Dependency Providers
def get_rag_service(): return rag_service
def get_repo(): return repo
def get_embed_service(): return embed_service