import subprocess
from typing import Tuple
from pathlib import Path

# Allowed command prefixes (add more as needed)
ALLOWED_COMMANDS = [
    "ls", "grep", "find", "cat", 
    "pwd", "python", "pip", "git"
]

# Safe directories (modify according to your needs)
SAFE_PATHS = [
    str(Path.home() / "projects"),
    str(Path.cwd()),
    "/tmp"
]

def is_allowed(cmd: str) -> bool:
    """Check if command is in allowlist and within safe paths"""
    if not any(cmd.strip().startswith(x) for x in ALLOWED_COMMANDS):
        return False
    
    # Path safety check for file operations
    for path in SAFE_PATHS:
        if f" {path}" in cmd or cmd.startswith(path):
            return True
    return not ("/" in cmd or ".." in cmd)

def run_safe(cmd: str, timeout: int = 30) -> Tuple[bool, str]:
    """
    Securely executes shell commands with:
    - Command allowlisting
    - Path restrictions
    - Timeout protection
    - Output sanitization
    """
    try:
        # Security checks
        if not is_allowed(cmd):
            return False, f"Command not allowed: {cmd.split()[0]}"
        
        # Execute
        result = subprocess.run(
            cmd,
            shell=False,  # Critical security change
            executable="/bin/bash",
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
            cwd=SAFE_PATHS[0]  # Restrict working directory
        )
        
        # Sanitize output
        output = result.stdout.replace("\x00", "").strip()
        return True, output
        
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.replace("\x00", "").strip()
        return False, f"Error {e.returncode}: {error_msg}"
    except Exception as e:
        return False, f"Security violation: {type(e).__name__}"