import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_TITLE: str = "BitHealth Technical Test"
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL")

settings = Settings()