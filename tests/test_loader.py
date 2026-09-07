from pathlib import Path

from app.loader import load_file, load_repository


def test_load_file_returns_structured_file_data(tmp_path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    source_directory = repository / "src"
    source_directory.mkdir()

    file_path = source_directory / "auth.py"
    file_content = "def login():\n    return True\n"
    file_path.write_text(file_content, encoding="utf-8")

    loaded_file = load_file(file_path, repository)

    assert loaded_file.relative_path == Path("src") / "auth.py"
    assert loaded_file.absolute_path == file_path
    assert loaded_file.extension == ".py"
    assert loaded_file.language == "python"
    assert loaded_file.content == file_content


def test_load_file_returns_unknown_file_data(tmp_path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    source_directory = repository / "src"
    source_directory.mkdir()

    file_path = source_directory / "auth.go"
    file_content = "def login():\n    return True\n"
    file_path.write_text(file_content, encoding="utf-8")

    loaded_file = load_file(file_path, repository)

    assert loaded_file.relative_path == Path("src") / "auth.go"
    assert loaded_file.absolute_path == file_path
    assert loaded_file.extension == ".go"
    assert loaded_file.language == "unknown"
    assert loaded_file.content == file_content




def test_load_repository_loads_all_supported_files(tmp_path):
    repository = tmp_path / "sample_repo"
    repository.mkdir()

    (repository / "main.py").write_text("print('hello')", encoding="utf-8")
    (repository / "notes.txt").write_text("ignore this", encoding="utf-8")

    docs = repository / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("# Guide", encoding="utf-8")

    loaded_files = load_repository(repository)

    assert {file.relative_path for file in loaded_files} == {
        Path("main.py"),
        Path("docs") / "guide.md",
    }