import requests
import json
from typing import List, Optional
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
            
            self.base_url = config.get("model", {}).get("api_url", "http://localhost:11434").rstrip('/')
            self.model_name = config.get("model", {}).get("name", "gemma3:12b")
            self.timeout = config.get("model", {}).get("timeout", 60)
            self.temperature = config.get("model", {}).get("temperature", 0.7)
            
        except Exception as e:
            print(f"⚠️ Config error: {e}. Using defaults")
            self.base_url = "http://localhost:11434"
            self.model_name = "gemma3:12b"
            self.timeout = 60
            self.temperature = 0.7

    def query_model(self, prompt: str, max_retries: int = 3) -> str:
        """Final corrected query method"""
        endpoints = [
            "/api/chat",  # Primary endpoint
            "/api/generate"  # Fallback endpoint
        ]
        
        for attempt in range(max_retries):
            for endpoint in endpoints:
                try:
                    # Prepare payload
                    if endpoint == "/api/chat":
                        payload = {
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "stream": False,
                            "options": {"temperature": self.temperature}
                        }
                    else:
                        payload = {
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"temperature": self.temperature}
                        }
                    
                    print(f"Attempt {attempt+1}: Sending to {self.base_url}{endpoint}")
                    
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Handle response
                    if endpoint == "/api/chat":
                        return result.get("message", {}).get("content", "").strip()
                    return result.get("response", "").strip()
                    
                except requests.exceptions.RequestException as e:
                    print(f"Attempt {attempt+1} on {endpoint} failed: {str(e)}")
                    continue
        
        return (
            "⚠️ All API attempts failed\n"
            "Successful curl test confirms API works - check:\n"
            "1. Your config.json 'api_url' should be: 'http://localhost:11434'\n"
            "2. No trailing slash in base URL\n"
            "3. Try the official ollama Python package:\n"
            "   pip install ollama\n"
            "   Then use ollama.chat() instead"
        )

    def _get_recent_context(self, max_items: int = 3) -> List[str]:
        """Get most relevant context snippets"""
        return self.context[-max_items:] if self.context else []

    def clear_context(self) -> None:
        """Reset conversation history"""
        self.context = []