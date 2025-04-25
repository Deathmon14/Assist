import requests
import json
from typing import List, Dict, Optional
from pathlib import Path

class CodingAgent:
    def __init__(self, config_path: str = "config.json"):
        self._load_config(config_path)
        self.context: List[str] = []
        self.last_response: Optional[str] = None

    def _load_config(self, config_path: str) -> None:
        """Load configuration with fallback defaults"""
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            self.base_url = config.get("model", {}).get("api_url", "http://localhost:11434/api")
            self.model_name = config.get("model", {}).get("name", "gemma3:12b")
            self.timeout = config.get("model", {}).get("timeout", 60)
            self.temperature = config.get("model", {}).get("temperature", 0.7)
            
        except Exception as e:
            print(f"⚠️ Config error: {e}. Using defaults")
            self.base_url = "http://localhost:11434/api"
            self.model_name = "gemma3:12b"
            self.timeout = 60
            self.temperature = 0.7

    def query_model(self, prompt: str, max_retries: int = 3) -> str:
        """Query Ollama with retries and context management"""
        self.context.append(f"User: {prompt}")
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_ctx": 4096,  # Context window size
                            "seed": 42  # For reproducibility
                        },
                        "context": self._get_recent_context()
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                self.last_response = result["response"].strip()
                self.context.append(f"Assistant: {self.last_response}")
                
                return self.last_response

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    return (
                        f"⚠️ Model query failed after {max_retries} attempts\n"
                        f"Error: {str(e)}\n"
                        f"Try:\n1. ollama serve\n2. ollama pull {self.model_name}"
                    )
                continue

    def _get_recent_context(self, max_items: int = 3) -> List[str]:
        """Get most relevant context snippets"""
        return self.context[-max_items:] if self.context else []

    def clear_context(self) -> None:
        """Reset conversation history"""
        self.context = []