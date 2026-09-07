# Codebase Intelligence Agent

A fully local, offline-capable codebase intelligence project. Its eventual goal
is to answer grounded questions about a software repository, such as where a
feature is implemented, which files use a dependency, or how a workflow works.

The project is deliberately built in small stages so that the underlying
concepts are understood before introducing larger AI frameworks.

## Current status

**Phase 1: Repository scanner** is complete.

The scanner recursively finds repository files relevant to code intelligence.
It supports common source, configuration, documentation, and schema file types,
while excluding generated files and dependency directories.

The Phase 1 test suite passes with coverage for supported and unsupported file
types, nested directories, ignored directories, and nonexistent paths.

Implemented files:

- `app/scanner.py` — repository scanning logic
- `tests/test_scanner.py` — automated scanner tests

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

The current tests cover supported files, unsupported files, nested directories,
ignored directories, and nonexistent repository paths.

## Using the scanner

```python
from app.scanner import scan_repository

files = scan_repository("C:/path/to/a/repository")

for file_path in files:
    print(file_path)
```

`scan_repository()` returns a list of `pathlib.Path` objects for relevant
files. It raises `FileNotFoundError` if the path does not exist and
`NotADirectoryError` if the provided path is a file rather than a directory.

## Development notes

Before running the test suite, make sure the scanner calls `path.is_file()`
with parentheses. `path.is_file` alone refers to the method itself rather than
checking whether the path is a file.

Repository contents may be proprietary. Do not commit indexed repositories,
virtual environments, caches, secrets, vector databases, or downloaded models.

## Roadmap

1. Repository scanner
2. File loading and basic line-based chunking
3. Local embeddings and cosine similarity
4. Local vector database
5. Manual retrieval-augmented generation pipeline
6. LangChain integration
7. Code-aware retrieval
8. LangGraph workflow and tools
9. Evaluation benchmark

Only Phase 1 is in scope right now. Future components will be added only after
the current phase is complete and tested.
