# Data Ingestion Guide — `ingest.py`

`scripts/ingest.py` O.T.T.O ka data pipeline tool hai. Yeh aapki files ko read karta hai, unhe chunks mein torata hai, vector embeddings banata hai, aur Qdrant mein store karta hai. Saath hi `knowledge_base.json` bhi automatically update ho jaata hai.

---

## Quick Start

```powershell
# Ek file
python scripts/ingest.py --path "C:\Users\admin\Documents\rules.pdf"

# folder
python scripts/ingest.py --path "C:\Users\admin\Documents\society_docs"

# Custom collection ke saath
python scripts/ingest.py --path "data\Smart Scociety\Financials & Accounts" --collection pro_rag_collection
```

---

## Arguments

| Argument | Zaruri? | Default | Description |
|----------|---------|---------|-------------|
| `--path` | Haan | — | File ya folder ka full path |
| `--collection` | Nahi | `pro_rag_collection` | Qdrant collection ka naam |

---

## Supported File Types

| Extension | Type |
|-----------|------|
| `.pdf` | PDF documents |
| `.txt` | Plain text files |
| `.md` | Markdown files |
| `.csv` | CSV / spreadsheet data |

---

## Pipeline Flow

```
Input Path (file ya folder)
        │
        ▼
   Files collect
        │
        ▼
  File read (PDF / TXT / MD / CSV)
        │
        ▼
  Text chunking
  (500 chars, 50 overlap)
        │
        ▼
  FastEmbed — BAAI/bge-small-en-v1.5
  (384-dim vectors)
        │
        ▼
  Qdrant upsert
  (UUID per chunk)
        │
        ▼
  knowledge_base.json update
```

---

## Example Output

```
=======================================================
  O.T.T.O Data Ingestion Pipeline
=======================================================
  Path       : data/Smart Scociety/Financials & Accounts
  Collection : pro_rag_collection
  Files found: 2
=======================================================

  -> Property_Tax_Guide.md
     14 chunks ingest ho gaye

  -> Surcharge_&_Arrears_Policy.md
     9 chunks ingest ho gaye

[kb] knowledge_base.json mein 2 nayi entries add hui

=======================================================
  DONE — 23 chunks 'pro_rag_collection' mein save
  Total in Qdrant now: 456 chunks
=======================================================
```

---

## Naya Data Add Karne Ka Process

### 1. Files tayyar karo

```
data/
└── Smart Scociety/
    └── New Category/          ← naya folder
        ├── new_document.md    ← files daalo
        └── policy.pdf
```

### 2. Docker chal raha ho tab bhi sirf yeh command kaafi hai

```powershell
python scripts/ingest.py --path "data\Smart Scociety\New Category"
```

Qdrant ka port `6335` expose hai — container ke andar jaane ki zaroorat nahi.

### 3. App restart nahi chahiye

Ingest hone ke baad O.T.T.O turant naye data se jawab dena shuru kar deta hai.

---

## Configuration (script ke andar)

| Variable | Value | Description |
|----------|-------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server address |
| `QDRANT_PORT` | `6335` | Qdrant port |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
| `VECTOR_SIZE` | `384` | Vector dimensions |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |

---

## Kya Automatically Hota Hai

| Kaam | Hota Hai? |
|------|-----------|
| Collection auto-create (agar nahi hai) | Yes |
| Duplicate chunks se bachao (UUID) | Yes |
| `knowledge_base.json` update | Yes |
| App restart | Nahi chahiye |
| Docker rebuild | Nahi chahiye |

---

## Common Errors

| Error | Wajah | Hal |
|-------|-------|-----|
| `Path exist nahi karti` | Path galat hai | Double-check karein, backslash `\` ki jagah `/` use karein |
| `Connection refused` | Qdrant band hai | `docker-compose up -d` chalayein |
| `PDF read error` | Corrupt / scanned PDF | Text-based PDF use karein |
| `Koi supported file nahi mili` | Extension supported nahi | `.pdf .txt .md .csv` mein se koi use karein |
