from sentence_transformers import SentenceTransformer
import random

class EmbeddingService:
    def __init__(self):
        # self.model_name = 'paraphrase-multilingual-MiniLM-L12-v2' # Model with 384 dimensions
        # self.model = SentenceTransformer(self.model_name)
        self.dimension = 384 # fake embedding dimension
        
    def get_embedding(self, text: str) -> list[float]:
        # # Menghasilkan list of floats
        # embedding = self.model.encode(text)
        # return embedding.tolist()
        random.seed(abs(hash(text)) % 10000)
        return [random.random() for _ in range(self.dimension)] # fake embedding