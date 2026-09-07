from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".tsx", ".jsx",
    ".sql", ".md", ".json", ".yaml", ".yml",
    ".xml", ".properties", ".toml",
}

IGNORED_DIRECTORIES = {
    ".git", "node_modules", "target", "build", "dist",
    "__pycache__", ".venv", "venv", ".idea", ".vscode",
}


def scan_repository(repo_path: str | Path) -> list[Path]:
    root = Path(repo_path)

    if not root.exists():
        raise FileNotFoundError(f"Repository path '{repo_path}' does not exist.")
        
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a Directory.")

    
    found_files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        if any(part in IGNORED_DIRECTORIES for part in relative_path.parts[:-1]):
            continue

        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            found_files.append(path)

    return found_files
    