import os
from groq import Groq # Pip install groq
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END

class GraphState(TypedDict):
    question: str
    context: List[str]
    answer: str

class RAGService:
    def __init__(self, repository, embedding_service):
        self.repo = repository
        self.embedder = embedding_service
        # Inisialisasi Groq Client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant" # Model Groq yang sangat cepat
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("fetch_context", self._retrieve_logic)
        workflow.add_node("generate_answer", self._answer_logic)
        
        workflow.set_entry_point("fetch_context")
        workflow.add_edge("fetch_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        return workflow.compile()

    def _retrieve_logic(self, state: GraphState) -> Dict[str, Any]:
        query = state["question"]
        vector = self.embedder.get_embedding(query)
        # Ambil dokumen dari Qdrant
        context = self.repo.search(vector, query)
        return {"context": context}

    def _answer_logic(self, state: GraphState) -> Dict[str, Any]:
        ctx = "\n".join(state.get("context", []))
        question = state["question"]
        
        if not ctx:
            return {"answer": "Maaf, informasi tersebut tidak ditemukan dalam dokumen saya."}

        # PROMPT UNTUK GENERATOR (LLM)
        prompt = f"""
        Anda adalah asisten AI yang membantu. Jawablah pertanyaan pengguna HANYA berdasarkan konteks yang disediakan.
        Jika jawaban tidak ada di konteks, katakan Anda tidak tahu.
        
        KONTEKS:
        {ctx}
        
        PERTANYAAN:
        {question}
        
        JAWABAN:"""

        # Panggil Groq untuk narasi jawaban
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # Biar jawabannya konsisten & tidak ngawur
        )
        
        return {"answer": completion.choices[0].message.content}

    def execute(self, question: str):
        return self.workflow.invoke({"question": question, "context": [], "answer": ""})