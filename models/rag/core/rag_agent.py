import os
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

class RAGAgent:
    def __init__(self):
        self.client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.qdrant = QdrantClient("localhost", port=6333)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "pro_rag_collection"

    def get_hierarchical_context(self, query):
        query_vector = self.model.encode(query).tolist()
        
        # 1. Search for most relevant child chunk
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=3
        ).points
        
        if not results:
            return ""

        # 2. Hierarchical Logic: Agar metadata mein 'parent_text' hai to wo uthao
        # Warna current text hi use karo. 
        context_list = []
        for hit in results:
            # Professional tip: Chunking ke waqt hum 'parent_text' payload mein save karte hain
            text = hit.payload.get('parent_text', hit.payload.get('text', ""))
            context_list.append(text)
            
        return "\n---\n".join(context_list)

    def generate(self, query):
        context = self.get_hierarchical_context(query)
        if not context:
            return "Mujhe database mein iske mutaliq kuch nahi mila."

        prompt = f"""
        You are a professional AI Assistant. Answer the question using ONLY the context provided below.
        Context:
        {context}
        
        Question: {query}
        """
        
        completion = self.client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return completion.choices[0].message.content