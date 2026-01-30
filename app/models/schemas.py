from pydantic import BaseModel

class QuestionRequest(BaseModel):
    # Schema untuk input pertanyaan
    question: str

class DocumentRequest(BaseModel):
    # Schema untuk input dokumen (knowledge) baru
    text: str