from dataclasses import dataclass
from pathlib import Path

from loader import LoadedFile, load_repository


@dataclass
class CodeChunk:
    file_path: Path
    language: str
    start_line: int
    end_line: int
    content: str


def chunk_file(
    loaded_file: LoadedFile,
    chunk_size: int = 50,
    overlap: int = 10,
) -> list[CodeChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be at least zero and smaller than chunk_size")

    lines = loaded_file.content.splitlines()

    if not lines:
        return []

    chunks = []
    step = chunk_size - overlap
    start_index = 0

    while start_index < len(lines):
        end_index = min(start_index + chunk_size, len(lines))
        chunk_lines = lines[start_index:end_index]

        chunks.append(
            CodeChunk(
                file_path=loaded_file.relative_path,
                language=loaded_file.language,
                start_line=start_index + 1,
                end_line=end_index,
                content="\n".join(chunk_lines),
            )
        )

        if end_index == len(lines):
            break

        start_index += step

    return chunks


def chunk_repository(
        repo_path: str | Path,
        chunk_size: int = 50,
        overlap: int = 10
) -> list[CodeChunk]:
    loaded_files = load_repository(repo_path)

    chunks = []

    for loaded_file in loaded_files:
        chunks.extend(
            chunk_file(
                loaded_file,
                chunk_size=chunk_size,
                overlap=overlap
            )
        )

    return chunks