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
        self.workflow = self._build_graph()

    def _build_graph(self):
        # Gunakan GraphState sebagai skema
        workflow = StateGraph(GraphState) 
        
        # PERBAIKAN: Nama node diubah agar tidak bentrok dengan nama channel di GraphState
        workflow.add_node("fetch_context", self._retrieve_logic)
        workflow.add_node("generate_answer", self._answer_logic)
        
        workflow.set_entry_point("fetch_context")
        workflow.add_edge("fetch_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        return workflow.compile()

    def _retrieve_logic(self, state: GraphState) -> Dict[str, Any]:
        query = state["question"]
        vector = self.embedder.get_embedding(query)
        context = self.repo.search(vector, query)
        return {"context": context}

    def _answer_logic(self, state: GraphState) -> Dict[str, Any]:
        ctx = state.get("context", [])
        answer = f"I found this: '{ctx[0][:100]}...'" if ctx else "Sorry, I don't know."
        return {"answer": answer}

    def execute(self, question: str):
        # Masukkan initial state yang lengkap
        return self.workflow.invoke({
            "question": question, 
            "context": [], 
            "answer": ""
        })