# utils/file_ops.py
from pathlib import Path

def read_file(path: str) -> str:
    path = Path(path).expanduser()  # Handles ~ and relative paths
    if not path.exists():
        return f"❌ File not found: {path}"
    
    with open(path, 'r') as f:
        return f"```{path.suffix[1:]}\n{f.read()}\n```"

def write_file(path: str, content: str):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
