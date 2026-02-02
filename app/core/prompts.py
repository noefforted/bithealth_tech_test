import textwrap

RAG_PROMPT_TEMPLATE = textwrap.dedent("""
    Anda adalah asisten AI yang membantu. Jawablah pertanyaan pengguna HANYA berdasarkan konteks yang disediakan.
    Jika jawaban tidak ada di konteks, katakan Anda tidak tahu.
    
    KONTEKS:
    {context}
    
    PERTANYAAN:
    {question}
    
    JAWABAN:
""").strip()