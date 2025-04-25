# utils/code_search.py
import subprocess
from pathlib import Path

def grep_codebase(pattern: str, path: str = ".") -> str:
    """Uses grep/fd to find code patterns"""
    result = subprocess.run(
        ["grep", "-n", pattern, "-r", path],
        capture_output=True, text=True
    )
    return result.stdout or "No matches found"