# Codebase Intelligence Agent

A fully local, offline-capable codebase intelligence project. Its eventual goal
is to answer grounded questions about a software repository, such as where a
feature is implemented, which files use a dependency, or how a workflow works.

The project is deliberately built in small stages so that the underlying
concepts are understood before introducing larger AI frameworks.

## Current status

- Phase 1: Repository scanner — complete
- Phase 2: File loading and basic chunking — complete
- Phase 3: Local embeddings and cosine similarity — complete
- Phase 4: Persistent local vector storage — complete

The current pipeline scans a local repository, loads supported files, splits
them into line-based chunks, turns text into local embedding vectors, and ranks
candidate text with persistent Qdrant vector search.

## Implemented files

- `app/scanner.py` — repository scanning logic
- `tests/test_scanner.py` — automated scanner tests
- `app/loader.py` — file-loading logic and `LoadedFile` metadata
- `tests/test_loader.py` — automated file-loading tests
- `app/chunker.py` — line-based chunking logic and `CodeChunk` metadata
- `tests/test_chunker.py` — automated chunking tests
- `app/embeddings.py` — local embeddings, cosine similarity, and top-K search
- `tests/test_embeddings.py` — automated embedding-math and search tests
- `app/vector_store.py` — persistent Qdrant indexing and vector search
- `tests/test_vector_store.py` — automated vector-store tests

## Supported file types

The scanner currently includes:

```text
.py  .java  .js  .ts  .tsx  .jsx
.sql .md    .json .yaml .yml .xml
.properties .toml
```

It ignores files under directories such as:

```text
.git  node_modules  target  build  dist
__pycache__  .venv  venv  .idea  .vscode
```

## Setup

Requirements:

- Python 3.13 or later
- Git
- A network connection for the one-time package and embedding-model download

Create and activate a virtual environment in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, allow it for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Running tests

With the virtual environment activated, run:

```powershell
python -m pytest -v
```

The tests cover scanner behavior, structured file loading, line-based chunking,
cosine-similarity math, and in-memory result ranking.

## Using the scanner

```python
from app.scanner import scan_repository

files = scan_repository("C:/path/to/a/repository")

for file_path in files:
    print(file_path)
```

`scan_repository()` returns relevant `pathlib.Path` objects. It raises
`FileNotFoundError` for a missing path and `NotADirectoryError` if given a file.

## Loading and chunking a repository

```python
from app.chunker import chunk_repository

chunks = chunk_repository(
    "C:/path/to/a/repository",
    chunk_size=50,
    overlap=10,
)

for chunk in chunks:
    print(chunk.file_path, chunk.start_line, chunk.end_line)
```

The loader adds each file's path, extension, language, and contents. The
chunker creates overlapping `CodeChunk` objects that retain file and line-range
metadata for later source attribution.

## Local embeddings and similarity search

The project uses the local `sentence-transformers/all-MiniLM-L6-v2` model.
On first use it downloads into `data/models/`; later runs reuse those local
files. The cache is ignored by Git.

```python
from app.embeddings import (
    embed_text,
    embed_texts,
    find_top_k_similar,
    load_embedding_model,
)

model = load_embedding_model()

documents = [
    "JWT authentication validates access tokens.",
    "Redis caches frequently requested data.",
]

document_embeddings = embed_texts(model, documents)
query_embedding = embed_text(model, "Where is token validation implemented?")

results = find_top_k_similar(query_embedding, document_embeddings, top_k=1)

for index, score in results:
    print(score, documents[index])
```

Embeddings are 384-dimensional vectors. Cosine similarity compares their
direction: higher scores indicate greater semantic relatedness. This search is
used to rank the results returned by the local vector database.

## Persistent local vector storage

Phase 4 uses Qdrant in persistent local mode. It runs inside the Python process
and stores its database files in `data/qdrant/`, so no server or Docker
container is required during development.

```python
from app.embeddings import embed_text, load_embedding_model
from app.vector_store import (
    get_client,
    index_repository,
    search_chunks,
)

client = get_client()
model = load_embedding_model()

index_repository(client, model, "C:/path/to/a/repository")

query_embedding = embed_text(
    model,
    "Where is JWT authentication implemented?",
)

results = search_chunks(client, query_embedding, top_k=3)

for result in results:
    print(
        result.score,
        result.file_path.as_posix(),
        result.start_line,
        result.end_line,
    )

client.close()
```

Each Qdrant point contains a 384-dimensional embedding plus payload metadata:
repository name, file path, language, line range, and chunk content. Qdrant
returns the nearest vectors along with this metadata, enabling later answers to
cite their source chunks.

## Development notes

Repository contents may be proprietary. Do not commit indexed repositories,
virtual environments, caches, secrets, vector databases, or downloaded models.
Both `data/models/` and `data/qdrant/` are ignored by Git.

## Roadmap

1. Repository scanner — complete
2. File loading and basic line-based chunking — complete
3. Local embeddings and cosine similarity — complete
4. Local vector database — complete
5. Manual retrieval-augmented generation pipeline
6. LangChain integration
7. Code-aware retrieval
8. LangGraph workflow and tools
9. Evaluation benchmark

The next milestone is Phase 5: a manual retrieval-augmented generation (RAG)
pipeline using the indexed repository context.
