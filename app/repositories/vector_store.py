import uuid
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
# from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self, url: str, collection_name: str, vector_size: int):
        self.collection_name = collection_name
        self.vector_size = vector_size
        # Inisialisasi Client dengan Fallback Otomatis
        self.client = self._connect(url)
        self._init_collection()

    def _connect(self, url: str) -> QdrantClient:
        try:
            client = QdrantClient(url=url, timeout=5)
            # Tes koneksi dengan cek collection
            client.get_collections()
            logger.info(f"Connected to Qdrant Sexrver at {url}")
            return client
        except Exception as e:
            logger.warning(f"Qdrant server unavailable ({e}). Falling back to Native In-Memory mode.")
            # Native in memery fallback
            return QdrantClient(":memory:")

    def _init_collection(self):
        # Memastikan koleksi siap digunakan
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.DOT
                )
            )
            logger.info(f"Collection '{self.collection_name}' initialized.")
        except Exception as e:
            logger.error(f"Critical error during collection initialization: {e}")

    def add(self, vector: list, text: str, doc_id: str = None):
        if not doc_id:
            doc_id = str(uuid.uuid4())
            
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(id=doc_id, vector=vector, payload={"text": text})]
            )
            logger.info(f"Stored document: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to upsert document: {e}")

    def search(self, vector: list, query_text: str, limit: int = 2):
        try:
            hits = self.client.search(
                collection_name=self.collection_name, 
                query_vector=vector, 
                limit=limit
            )
            
            # Threshold disesuaikan dengan Dot Product
            threshold = 6.0 
            relevant_texts = []

            for hit in hits:
                logger.info(f"Score: {hit.score:.4f} | Data: {hit.payload.get('text', '')[:30]}...")
                if hit.score >= threshold:
                    relevant_texts.append(hit.payload["text"])
            
            return relevant_texts
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []