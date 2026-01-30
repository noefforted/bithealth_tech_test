from sentence_transformers import SentenceTransformer
import torch

class EmbeddingService:
    def __init__(self):
        # Kita gunakan model multilingual agar jago Bahasa Indonesia
        # Model ini menghasilkan 384 dimensi
        self.model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
        self.model = SentenceTransformer(self.model_name)
        
    def get_embedding(self, text: str) -> list[float]:
        """
        Menghasilkan vektor semantik sungguhan menggunakan model AI.
        """
        # Menghasilkan list of floats
        embedding = self.model.encode(text)
        return embedding.tolist()