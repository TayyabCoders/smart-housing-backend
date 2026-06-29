import streamlit as st
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_HOST  = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT  = int(os.getenv("QDRANT_PORT", 6333))

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found! Check your .env file.")
    st.stop()


@st.cache_resource
def init_clients():
    client       = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    embedder     = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    groq_client  = Groq(api_key=GROQ_API_KEY)
    return client, embedder, groq_client


client, embedder, groq_client = init_clients()


def get_all_collections() -> list[str]:
    try:
        return sorted([c.name for c in client.get_collections().collections])
    except Exception:
        return []


def get_context(query: str, collections: list[str]) -> str:
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
    system_prompt = f"""You are O.T.T.O, a professional AI assistant for Smart Society residents.
Use the provided context to answer accurately. If the context doesn't contain the answer, say so politely.

CONTEXT:
{context}"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": query},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {str(e)}"


# ── UI ────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="O.T.T.O | RAG Assistant", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("🗂️ Knowledge Base")
    st.markdown("---")

    all_collections = get_all_collections()

    if not all_collections:
        st.warning("No collections found in Qdrant.\nRun the ingest script first.")
        selected_collections = []
    else:
        select_all = st.checkbox("Search All Collections", value=True)

        if select_all:
            selected_collections = all_collections
            st.caption(f"{len(all_collections)} collections active")
        else:
            selected_collections = st.multiselect(
                "Pick collections:",
                options=all_collections,
                default=all_collections[:1] if all_collections else [],
            )

    st.markdown("---")
    st.caption("Active collections:")
    for col in selected_collections:
        st.markdown(f"• `{col}`")

st.title("🤖 O.T.T.O: Smart Society RAG Assistant")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask O.T.T.O..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("O.T.T.O is thinking..."):
        context      = get_context(prompt, selected_collections)
        full_response = get_otto_response(prompt, context)

    with st.chat_message("assistant"):
        st.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
