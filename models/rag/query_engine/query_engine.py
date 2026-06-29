import json
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient

KB_PATH = Path(__file__).parent / "knowledge_base.json"

with open(KB_PATH, encoding="utf-8") as f:
    KB = json.load(f)["knowledge_base"]

COLLECTION = KB["collection"]
embedder = TextEmbedding(model_name=KB["embed_model"])
qdrant = QdrantClient("localhost", port=6333)


def get_categories() -> list[str]:
    return [c["name"] for c in KB["categories"]]


def get_topics(category: str) -> list[str]:
    for cat in KB["categories"]:
        if cat["name"] == category:
            return [doc["topic"] for doc in cat["documents"]]
    return []


def search(query: str, limit: int = 3) -> list[dict]:
    query_vector = list(embedder.embed([query]))[0].tolist()
    results = qdrant.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=limit,
    ).points
    return [
        {
            "score": round(r.score, 4),
            "text": r.payload.get("page_content", r.payload.get("text", "")),
            "source": r.payload.get("filename", "unknown"),
            "category": r.payload.get("metadata", {}).get("category", ""),
        }
        for r in results
    ]


if __name__ == "__main__":
    print(f"Knowledge Base: {KB['name']}")
    print(f"Categories ({len(KB['categories'])}):", get_categories())

    q = "maintenance fee charges"
    print(f"\nQuery: '{q}'")
    for i, r in enumerate(search(q), 1):
        print(f"  {i}. [{r['score']}] {r['source']}")
        print(f"     {r['text'][:120]}...")
