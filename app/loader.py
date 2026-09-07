from dataclasses import dataclass
from pathlib import Path
from app.scanner import scan_repository


@dataclass
class LoadedFile:
    relative_path: Path
    absolute_path: Path
    extension: str
    language: str
    content: str

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".sql": "sql",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".xml": "xml",
    ".properties": "properties",
    ".toml": "toml",
}


def load_file(file_path: str | Path, repository_root: str | Path) -> LoadedFile:

    file_path = Path(file_path)
    repository_root = Path(repository_root)

    content = file_path.read_text(encoding="utf-8")

    relative_path = file_path.relative_to(repository_root)
    extension = file_path.suffix.lower()
    language = LANGUAGE_BY_EXTENSION.get(extension, "unknown")

    return LoadedFile(
        relative_path=relative_path,
        absolute_path=file_path,
        extension=extension,
        language=language,
        content=content,
    )


def load_repository(repo_path: str | Path) -> list[LoadedFile]:
    repository_root = Path(repo_path)
    file_paths = scan_repository(repository_root)

    return[load_file(file_path, repository_root) for file_path in file_paths]