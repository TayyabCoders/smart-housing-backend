"""
Data Ingestion Script — Qdrant mein data daalo, har directory apni collection mein

Usage:
    # Single directory → auto collection name from dir name
    python scripts/ingest.py --path "data/Smart Scociety/Sports & Recreation"

    # Single directory → custom collection name
    python scripts/ingest.py --path "data/Smart Scociety/Financials & Accounts" --collection my_finance

    # ALL subdirectories at once → each gets its own auto-named collection
    python scripts/ingest.py --all --path "data/Smart Scociety"
"""

import argparse
import json
import re
import uuid
from pathlib import Path

from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models

QDRANT_HOST   = "localhost"
QDRANT_PORT   = 6335
EMBED_MODEL   = "BAAI/bge-small-en-v1.5"
VECTOR_SIZE   = 384
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
SUPPORTED_EXT = {".pdf", ".txt", ".md", ".csv"}

KB_PATH = Path(__file__).parent.parent / "query_engine" / "knowledge_base.json"


# ── helpers ───────────────────────────────────────────────────────────────────

def dir_to_collection(dir_name: str) -> str:
    """'Sports & Recreation' → 'sports_recreation'"""
    name = dir_name.lower()
    name = re.sub(r"[&\s]+", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def read_file(file: Path) -> str:
    ext = file.suffix.lower()
    if ext == ".pdf":
        try:
            reader = PdfReader(str(file))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            print(f"     [!] PDF read error — {file.name}: {e}")
            return ""
    if ext in {".txt", ".md", ".csv"}:
        return file.read_text(encoding="utf-8", errors="ignore")
    return ""


def collect_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() in SUPPORTED_EXT else []
    files = []
    for ext in SUPPORTED_EXT:
        files.extend(input_path.rglob(f"*{ext}"))
    return sorted(files)


# ── knowledge_base.json updater ───────────────────────────────────────────────

def update_knowledge_base(new_files: list[Path], collection: str):
    if not KB_PATH.exists():
        kb = {"knowledge_base": {
            "name": "Smart Society Knowledge Base",
            "embed_model": EMBED_MODEL,
            "categories": []
        }}
    else:
        kb = json.loads(KB_PATH.read_text(encoding="utf-8"))

    existing_paths = {
        doc["path"]
        for cat in kb["knowledge_base"]["categories"]
        for doc in cat["documents"]
    }

    added = 0
    for file in new_files:
        rel = str(file).replace("\\", "/")
        if rel in existing_paths:
            continue

        category_name = file.parent.name
        topic = file.stem.replace("_", " ").replace("-", " ")

        category = next(
            (c for c in kb["knowledge_base"]["categories"] if c["name"] == category_name),
            None,
        )
        if category is None:
            category = {"name": category_name, "collection": collection, "document_count": 0, "documents": []}
            kb["knowledge_base"]["categories"].append(category)

        category["documents"].append({
            "filename": file.name,
            "path": rel,
            "topic": topic,
            "type": file.suffix.lstrip("."),
            "collection": collection,
        })
        category["document_count"] = len(category["documents"])
        added += 1

    if added:
        KB_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[kb] {added} nayi entries added to knowledge_base.json\n")
    else:
        print(f"[kb] knowledge_base.json already up-to-date\n")


# ── core ingest function ──────────────────────────────────────────────────────

def ingest(input_path_str: str, collection: str):
    input_path = Path(input_path_str)

    if not input_path.exists():
        print(f"[!] Path does not exist: {input_path_str}")
        return

    files = collect_files(input_path)
    if not files:
        print(f"[!] No supported files found. Supported: {', '.join(SUPPORTED_EXT)}")
        return

    print(f"\n{'='*55}")
    print(f"  O.T.T.O Ingestion Pipeline")
    print(f"{'='*55}")
    print(f"  Path       : {input_path_str}")
    print(f"  Collection : {collection}")
    print(f"  Files      : {len(files)}")
    print(f"{'='*55}\n")

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    embedder = TextEmbedding(model_name=EMBED_MODEL)
    client   = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
        print(f"[+] Created collection '{collection}'\n")
    else:
        info = client.get_collection(collection)
        print(f"[i] Collection '{collection}' exists — {info.points_count} chunks already stored\n")

    total_chunks = 0
    ingested_files = []

    for file in files:
        print(f"  -> {file.name}")
        text = read_file(file)

        if not text.strip():
            print(f"     [skip] empty file\n")
            continue

        chunks  = splitter.split_text(text)
        vectors = list(embedder.embed(chunks))

        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec.tolist(),
                payload={
                    "page_content": chunk,
                    "source":       str(file),
                    "filename":     file.name,
                    "category":     file.parent.name,
                },
            )
            for chunk, vec in zip(chunks, vectors)
        ]

        client.upsert(collection_name=collection, points=points)
        total_chunks += len(points)
        ingested_files.append(file)
        print(f"     {len(points)} chunks ingested\n")

    if ingested_files:
        update_knowledge_base(ingested_files, collection)

    print(f"{'='*55}")
    print(f"  DONE — {total_chunks} chunks saved to '{collection}'")
    print(f"  Total in Qdrant: {client.get_collection(collection).points_count} chunks")
    print(f"{'='*55}\n")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="O.T.T.O — Qdrant Data Ingestion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest one directory (collection name auto-derived from dir name)
  python scripts/ingest.py --path "data/Smart Scociety/Sports & Recreation"

  # Ingest one directory with custom collection name
  python scripts/ingest.py --path "data/Smart Scociety/Financials & Accounts" --collection finance

  # Ingest ALL subdirectories — each gets its own collection
  python scripts/ingest.py --all --path "data/Smart Scociety"
        """,
    )
    parser.add_argument("--path", required=True, help="File or folder path to ingest")
    parser.add_argument("--collection", default=None, help="Collection name (auto-derived from dir name if omitted)")
    parser.add_argument("--all", action="store_true", dest="ingest_all",
                        help="Ingest each immediate subdirectory as its own collection")
    args = parser.parse_args()

    root = Path(args.path)

    if args.ingest_all:
        if not root.is_dir():
            print(f"[!] --all requires a directory path, got: {args.path}")
            return
        subdirs = sorted([d for d in root.iterdir() if d.is_dir()])
        if not subdirs:
            print(f"[!] No subdirectories found in: {args.path}")
            return
        print(f"\nFound {len(subdirs)} directories — ingesting each into its own collection...\n")
        for subdir in subdirs:
            col = dir_to_collection(subdir.name)
            ingest(str(subdir), col)
    else:
        if args.collection:
            col = args.collection
        else:
            col = dir_to_collection(root.name) if root.is_dir() else dir_to_collection(root.parent.name)
        ingest(args.path, col)


if __name__ == "__main__":
    main()
