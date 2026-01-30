import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self, url: str, collection_name: str, vector_size: int): # Tambahkan vector_size
        self.collection_name = collection_name
        self.vector_size = vector_size  # Simpan sebagai variabel kelas
        self.memory_fallback = []
        try:
            self.client = QdrantClient(url)
            self._init_collection()
            self.is_active = True
            logger.info("Berhasil terhubung ke Qdrant.")
        except Exception as e:
            self.is_active = False
            logger.warning(f"Qdrant offline, menggunakan fallback: {e}")

    def _init_collection(self):
        # ... logika pengecekan koleksi ...
        # GUNAKAN variabel dari constructor di sini:
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,  # <-- SEKARANG INI DINAMIS DARI .ENV
                distance=Distance.DOT
            )
        )

    def add(self, vector: list, text: str, doc_id: str = None):
            # Jika doc_id tidak diberikan, buat UUID otomatis
            if not doc_id:
                doc_id = str(uuid.uuid4())
                
            if self.is_active:
                try:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=[PointStruct(id=doc_id, vector=vector, payload={"text": text})]
                    )
                    logger.info(f"Berhasil menyimpan dokumen dengan ID: {doc_id}")
                except Exception as e:
                    logger.error(f"Gagal upsert ke Qdrant: {e}")
                    # Fallback jika upsert gagal
                    self.memory_fallback.append({"id": doc_id, "text": text, "vector": vector})
            else:
                # Fallback jika Qdrant memang sedang tidak aktif
                self.memory_fallback.append({"id": doc_id, "text": text, "vector": vector})

    def search(self, vector: list, query_text: str, limit: int = 2):
            if self.is_active:
                try:
                    hits = self.client.search(
                        collection_name=self.collection_name, 
                        query_vector=vector, 
                        limit=limit
                    )
                    
                    threshold = 6
                    relevant_texts = []

                    for hit in hits:
                        # Log ini HARUS sejajar di sini agar selalu muncul di terminal
                        # Kita ambil 20 karakter pertama teksnya agar log rapi
                        snippet = hit.payload.get("text", "")[:20]
                        logger.info(f"📊 SKOR: {hit.score:.4f} | DOKUMEN: {snippet}...")

                        if hit.score >= threshold:
                            relevant_texts.append(hit.payload["text"])
                    
                    return relevant_texts
                except Exception as e:
                    logger.error(f"Gagal search di Qdrant: {e}")
                    return []
            
            # Fallback search
            return [d["text"] for d in self.memory_fallback if query_text.lower() in d["text"].lower()][:limit]