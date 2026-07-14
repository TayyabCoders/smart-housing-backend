"""
O.T.T.O retrieval + generation engine — shared by api.py.
Ported from the original Streamlit app.py (now removed) with the
@st.cache_resource / st.error / st.stop calls swapped for plain Python.
"""
import os

from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from fastembed import TextEmbedding

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found! Check your .env file.")

_client: QdrantClient | None = None
_embedder: TextEmbedding | None = None
_groq_client: Groq | None = None


def init_clients() -> tuple[QdrantClient, TextEmbedding, Groq]:
    global _client, _embedder, _groq_client
    if _client is None:
        _client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        _embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _client, _embedder, _groq_client


def get_all_collections() -> list[str]:
    client, _, _ = init_clients()
    try:
        return sorted([c.name for c in client.get_collections().collections])
    except Exception:
        return []


def get_context(query: str, collections: list[str]) -> str:
    client, embedder, _ = init_clients()
    if not collections:
        return "No collections selected."
    try:
        query_vector = list(embedder.embed([query]))[0].tolist()
        context_parts = []
        for col in collections:
            try:
                results = client.query_points(
                    collection_name=col,
                    query=query_vector,
                    limit=2,
                ).points
                for r in results:
                    content = r.payload.get("page_content", "")
                    if content:
                        context_parts.append(f"[{col}]\n{content}")
            except Exception:
                continue
        return "\n\n".join(context_parts) if context_parts else "No relevant context found."
    except Exception as e:
        return f"Retrieval Error: {str(e)}"


def get_otto_response(query: str, context: str) -> str:
    _, _, groq_client = init_clients()
    system_prompt = f"""You are O.T.T.O, a professional AI assistant for Smart Society residents.
Use the provided context to answer accurately. If the context doesn't contain the answer, say so politely.

CONTEXT:
{context}"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {str(e)}"


def ask(query: str, collections: list[str] | None = None) -> dict:
    cols = collections if collections else get_all_collections()
    context = get_context(query, cols)
    answer = get_otto_response(query, context)
    return {"answer": answer, "collections_used": cols}
