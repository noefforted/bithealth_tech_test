import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_TITLE: str = "BitHealth Technical Test"
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "demo_collection")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", 384))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()