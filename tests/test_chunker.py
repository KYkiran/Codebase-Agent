from pathlib import Path

from app.chunker import chunk_file, chunk_repository
from app.loader import LoadedFile
import pytest


def test_chunk_file_splits_lines_with_overlap():
    content = "\n".join(f"line {number}" for number in range(1, 11))

    loaded_file = LoadedFile(
        relative_path=Path("src/example.py"),
        absolute_path=Path("/example/src/example.py"),
        extension=".py",
        language="python",
        content=content,
    )

    chunks = chunk_file(
        loaded_file,
        chunk_size=5,
        overlap=2,
    )

    assert len(chunks) == 3

    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 5
    assert chunks[0].content == "\n".join(
        ["line 1", "line 2", "line 3", "line 4", "line 5"]
    )

    assert chunks[1].start_line == 4
    assert chunks[1].end_line == 8
    assert chunks[1].content == "\n".join(
        ["line 4", "line 5", "line 6", "line 7", "line 8"]
    )

    assert chunks[2].start_line == 7
    assert chunks[2].end_line == 10
    assert chunks[2].content == "\n".join(
        ["line 7", "line 8", "line 9", "line 10"]
    )


def test_chunk_file_returns_empty_list_for_empty_content():
    loaded_file = LoadedFile(
        relative_path=Path("empty.py"),
        absolute_path=Path("/example/empty.py"),
        extension=".py",
        language="python",
        content="",
    )

    assert chunk_file(loaded_file) == []


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (5, -1),
        (5, 5),
        (5, 6),
    ],
)
def test_chunk_file_rejects_invalid_configuration(chunk_size, overlap):
    loaded_file = LoadedFile(
        relative_path=Path("example.py"),
        absolute_path=Path("/example/example.py"),
        extension=".py",
        language="python",
        content="line 1",
    )

    with pytest.raises(ValueError):
        chunk_file(
            loaded_file,
            chunk_size=chunk_size,
            overlap=overlap,
        )


def test_chunk_repository_chunks_supported_files(tmp_path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    (repository / "main.py").write_text(
        "line 1\nline 2\nline 3\nline 4",
        encoding="utf-8",
    )
    (repository / "ignore.txt").write_text(
        "this should not be loaded",
        encoding="utf-8",
    )

    chunks = chunk_repository(
        repository,
        chunk_size=2,
        overlap=0,
    )

    assert len(chunks) == 2
    assert {chunk.file_path for chunk in chunks} == {Path("main.py")}
    assert [(chunk.start_line, chunk.end_line) for chunk in chunks] == [
        (1, 2),
        (3, 4),
    ]