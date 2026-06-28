# O.T.T.O — Smart Society RAG Assistant
### User Guide

> **O.T.T.O** (Official Task & Training Operator) is a Retrieval-Augmented Generation (RAG) system built for Smart Society management. It answers resident queries using your own knowledge base, powered by **Groq LLM + Qdrant Vector DB + FastEmbed**.

---

## Project Structure

```
otto-rag/
│
├── app.py                          # Entry point — Streamlit chat UI
│
├── core/                           # Core RAG logic
│   ├── prompts.py                  # O.T.T.O system personality & prompt
│   ├── rag_agent.py                # RAG agent (retrieval + generation)
│   └── mcp_server.py               # MCP tool server (Claude integration)
│
├── pipeline/                       # Kafka streaming pipeline
│   ├── producer.py                 # Sends data to Kafka topic
│   └── consumer.py                 # Reads Kafka, embeds & stores in Qdrant
│
├── query_engine/                   # Search & retrieval engine
│   ├── query_engine.py             # Vector search logic
│   └── knowledge_base.json         # Index of all knowledge base documents
│
├── scripts/                        # Utility scripts
│   ├── ingest.py                   # Bulk data ingestion to Qdrant
│   └── setup.py                    # Auto-install & launch helper
│
├── data/                           # Knowledge base documents
│   └── Smart Society/
│       ├── Administrative & Legal/
│       ├── Archive & Future Developments/
│       ├── Community & Lifestyle/
│       ├── Digital Services & Smart App/
│       ├── Financials & Accounts/
│       ├── Infrastructure & Security/
│       └── Operations & Utilities/
│
├── docker-compose.yaml             # Qdrant + Kafka services
├── dockerfile                      # Docker image for the app
├── pyproject.toml                  # Python project config (uv)
├── requirements.txt                # Python dependencies
├── .env                            # Secret keys (never commit this)
└── USER_GUIDE.md                   # This file
```

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| Docker Desktop | Latest | Qdrant + Kafka |
| uv | Latest | Fast package manager |

---

## Step 1 — Environment Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=pro_rag_collection
```

Get your free Groq API key from: [console.groq.com](https://console.groq.com)

---

## Step 2 — Install Dependencies

```bash
# Using uv (recommended)
uv sync

# OR using pip
pip install -r requirements.txt
```

---

## Step 3 — Start Infrastructure (Docker)

```bash
docker-compose up -d
```

This starts:
- **Qdrant** on `http://localhost:6333` — Vector database
- **Kafka** on `localhost:9092` — Message streaming

Verify containers are running:
```bash
docker ps
```

---

## Step 4 — Ingest Your Data

Load your documents into Qdrant so O.T.T.O can answer from them.

**Option A — From a folder path:**
```bash
python scripts/ingest.py --path "C:\path\to\your\documents"
```

**Option B — From a specific file:**
```bash
python scripts/ingest.py --path "C:\path\to\file.pdf"
```

**Option C — Custom collection name:**
```bash
python scripts/ingest.py --path "C:\your\docs" --collection my_collection
```

Supported file types: `.pdf`, `.txt`, `.md`, `.csv`

---

## Step 5 — Run the Application

```bash
# Using uv
uv run app.py

# OR using Python directly
python app.py
```

Open your browser at: **http://localhost:8501**

---

## Using the Chat Interface

Once the app is running, simply type your question in the chat box.

**Example queries:**
- `What are the maintenance fee charges?`
- `How do I resolve a dispute with a neighbor?`
- `What is the security gate contact number?`
- `Tell me about property tax rules`
- `What facilities does the society have?`

O.T.T.O will search the knowledge base and provide answers based on your documents. If information is not found, it will direct you to the Admin Office.

---

## Running the Kafka Pipeline (Optional)

The Kafka pipeline allows real-time data streaming into Qdrant.

**Start the consumer** (listens for new data):
```bash
python pipeline/consumer.py
```

**Send data via producer:**
```bash
python pipeline/producer.py
```

---

## Using the MCP Server (Claude Integration)

O.T.T.O can be connected to Claude as a tool via the MCP server:

```bash
python core/mcp_server.py
```

This exposes `ask_my_knowledge_base` as a callable tool for Claude.

---

## Query Engine (Direct Search)

Test Qdrant search directly without the UI:

```bash
python query_engine/query_engine.py
```

View all available categories and documents:
```bash
python -c "from query_engine.query_engine import get_categories; print(get_categories())"
```

---

## Docker Deployment

Build and run the entire app in Docker:

```bash
# Build image
docker build -t otto-rag .

# Run container
docker run -p 8501:8501 --env-file .env otto-rag
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `GROQ_API_KEY not found` | Check `.env` file exists and has the correct key |
| `Qdrant connection refused` | Run `docker-compose up -d` first |
| `Collection not found` | Run `scripts/ingest.py` to create and populate collection |
| `QdrantClient has no attribute 'search'` | Use `query_points()` — old API removed in qdrant-client v1.7+ |
| Docker image not found | Run `docker-compose pull` then `docker-compose up -d` |

---

## Tech Stack

```
User Query
    │
    ▼
Streamlit UI  (app.py)
    │
    ▼
FastEmbed     (BAAI/bge-small-en-v1.5)   — query embedding
    │
    ▼
Qdrant        (vector search, top-3 docs)
    │
    ▼
Groq LLM      (llama-3.1-8b-instant)     — answer generation
    │
    ▼
Response
```

---

## Knowledge Base Structure

33 documents across 7 categories:

| Category | Documents |
|----------|-----------|
| Administrative & Legal | 4 |
| Archive & Future Developments | 2 |
| Community & Lifestyle | 14 |
| Digital Services & Smart App | 2 |
| Financials & Accounts | 2 |
| Infrastructure & Security | 4 |
| Operations & Utilities | 5 |

---

*Built by Hanzala Rashid — O.T.T.O Smart Society Assistant*
