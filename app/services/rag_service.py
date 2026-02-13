import os
import logging
from typing import Dict, Any, List, TypedDict
from groq import Groq
from langgraph.graph import StateGraph, END
from app.core.prompts import RESPONSE_PROMPT

# Setup logging untuk tracking error
logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    question: str
    context: List[str]
    answer: str

class RAGService:
    def __init__(self, repository, embedding_service):
        self.repo = repository
        self.embedder = embedding_service
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = os.getenv("GROQ_MODEL", "groq-compound")
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        # Nama method diubah ke suffix _node agar standar dengan LangGraph
        workflow.add_node("fetch_context", self._retrieve_node)
        workflow.add_node("generate_answer", self._generate_node)
        
        workflow.set_entry_point("fetch_context")
        workflow.add_edge("fetch_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        return workflow.compile()

    def _retrieve_node(self, state: GraphState) -> Dict[str, Any]:
        # Logika untuk mengambil data dari vector store
        try:
            query = state["question"]
            vector = self.embedder.get_embedding(query)
            context = self.repo.search(vector, query)
            return {"context": context}
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"context": []}

    def _generate_node(self, state: GraphState) -> Dict[str, Any]:
        # Logika untuk menghasilkan jawaban via LLM
        ctx_list = state.get("context", [])
        question = state["question"]
        
        if not ctx_list:
            return {"answer": "Maaf, informasi tersebut tidak ditemukan dalam dokumen saya."}

        # Menggunakan template eksternal
        context_str = "\n".join(ctx_list)
        prompt = RESPONSE_PROMPT.format(context=context_str, question=question)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return {"answer": completion.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return {"answer": "Maaf, terjadi kesalahan teknis saat menghubungi AI."}

    def execute(self, question: str):
        # Inisialisasi state awal dengan clean
        return self.workflow.invoke({
            "question": question, 
            "context": [], 
            "answer": ""
        })