import subprocess
import re
from pathlib import Path
from .model import CodingAgent
from utils import code_search, file_ops
from typing import Tuple

agent = CodingAgent()

def sanitize_input(text: str) -> str:
    """Remove potentially dangerous shell characters"""
    return re.sub(r"[;&|$`]", "", text.strip())

def run_safe(cmd: str) -> Tuple[bool, str]:
    """Secure command execution"""
    try:
        result = subprocess.run(
            sanitize_input(cmd),
            shell=True,
            check=True,
            timeout=60,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"

def handle_command(raw_input: str) -> str:
    try:
        # Pre-process input
        clean_input = sanitize_input(raw_input)
        
        if not clean_input:
            return "⚠️ Empty input"
            
        # Command routing
        if clean_input.startswith(("search", "find")):
            pattern = clean_input.split(" ", 1)[1]
            return code_search.grep_codebase(pattern)
            
        elif clean_input.startswith("explain"):
            filepath = clean_input.split(" ", 1)[1]
            code = file_ops.read_file(filepath)
            response = agent.query_model(
                f"Explain this code concisely:\n{code}\n"
                "Focus on key functionality and architecture."
            )
            return response[:2000]  # Limit response length
            
        elif clean_input.startswith("run "):
            cmd = clean_input.split(" ", 1)[1]
            success, output = run_safe(cmd)
            return output if success else f"🚨 {output}"
            
        elif clean_input.startswith("edit "):
            parts = clean_input.split(" ", 2)
            if len(parts) < 3:
                return "⚠️ Usage: edit <filepath> <instructions>"
                
            filepath, instructions = parts[1], parts[2]
            current_content = file_ops.read_file(filepath)
            new_content = agent.query_model(
                f"Rewrite this file exactly as requested. "
                f"Preserve all functionality.\n\n"
                f"Instructions: {instructions}\n\n"
                f"Current file:\n```\n{current_content}\n```"
            )
            file_ops.write_file(filepath, new_content)
            return f"✅ Updated {filepath}"
            
        else:
            # General query with context guidance
            response = agent.query_model(
                f"You are a coding assistant. Respond concisely to:\n"
                f"{clean_input}\n"
                "Provide code examples where applicable."
            )
            return response[:2000]

    except Exception as e:
        return (
            f"🚨 Critical error: {str(e)}\n"
            "Check:\n"
            "1. Ollama is running (ollama serve)\n"
            "2. Model is loaded (ollama list)\n"
            "3. File permissions"
        )

# Example usage for testing
if __name__ == "__main__":
    print(handle_command("explain agent/actions.py"))