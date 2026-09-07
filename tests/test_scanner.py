from app.scanner import scan_repository
from pathlib import Path
import pytest


def test_scan_repository_returns_supported_files(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    (repo / "app.py").write_text("print('hello')")
    (repo / "notes.txt").write_text("not source code")

    src = repo / "src"
    src.mkdir()
    (src / "service.py").write_text("def run(): pass")

    result = scan_repository(repo)

    relative_results = {path.relative_to(repo) for path in result}

    assert relative_results == {
        Path("app.py"),
        Path("src") / "service.py",
    }


def test_scan_repository_excludes_unsupported_files(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    (repo / "code.py").write_text("print('ok')")
    (repo / "image.png").write_bytes(b"not a real image")

    result = scan_repository(repo)

    assert {path.relative_to(repo) for path in result} == {Path("code.py")}


def test_scan_repository_skips_ignored_directories(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    (repo / "main.py").write_text("print('ok')")

    node_modules = repo / "node_modules"
    node_modules.mkdir()
    (node_modules / "dependency.js").write_text("console.log('ignore')")

    result = scan_repository(repo)

    assert {path.relative_to(repo) for path in result} == {Path("main.py")}


import pytest


def test_scan_repository_raises_for_missing_path(tmp_path):
    missing_repo = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError):
        scan_repository(missing_repo)