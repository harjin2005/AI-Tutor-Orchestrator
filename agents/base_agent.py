from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
import logging
from groq import Groq
import httpx
import asyncio

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # OpenRouter configuration with multiple fallback models
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        # Load multiple models from .env
        self.openrouter_models = self._load_fallback_models()
        self.current_model_index = 0
        
        # HTTPX client configuration
        self.timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
        self.limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        self._http_client: Optional[httpx.AsyncClient] = None

    def _load_fallback_models(self) -> List[str]:
        """Load multiple fallback models from environment variables"""
        models = []
        
        # Try to load OPENROUTER_MODEL_1, OPENROUTER_MODEL_2, etc.
        for i in range(1, 10):  # Support up to 10 models
            model = os.getenv(f"OPENROUTER_MODEL_{i}")
            if model:
                models.append(model)
                logger.info(f"Loaded fallback model {i}: {model}")
        
        # If no numbered models, use default
        if not models:
            default_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2-7b-instruct:free")
            models.append(default_model)
            logger.info(f"Using default model: {default_model}")
        
        return models

    async def get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=self.limits,
                follow_redirects=True
            )
        return self._http_client

    async def close_http_client(self):
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    @abstractmethod
    async def process(self, query: str) -> Dict[str, Any]:
        pass

    async def call_groq(self, prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
        try:
            if not self.groq_client.api_key or self.groq_client.api_key.startswith("gsk_your"):
                logger.warning("Groq API key not configured properly, using demo response")
                return self._get_demo_groq_response(prompt)
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content if content else self._get_demo_groq_response(prompt)
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}, using demo fallback")
            return self._get_demo_groq_response(prompt)

    async def call_openrouter(self, prompt: str, max_retries_per_model: int = 2) -> str:
        """Call OpenRouter with multiple model fallbacks"""
        
        if not self.openrouter_key or self.openrouter_key.startswith("sk-or-v1-your"):
            logger.warning("OpenRouter API key not configured, using demo response")
            return self._get_demo_openrouter_response(prompt)
        
        # Try each model in the fallback list
        for model_attempt, model in enumerate(self.openrouter_models):
            logger.info(f"Trying model {model_attempt + 1}/{len(self.openrouter_models)}: {model}")
            
            # Try each model with retries
            for retry in range(max_retries_per_model):
                try:
                    client = await self.get_http_client()
                    
                    response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openrouter_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:8000",
                            "X-Title": "AI Tutor Orchestrator"
                        },
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 1000,
                            "temperature": 0.7
                        }
                    )

                    # Handle rate limiting
                    if response.status_code == 429:
                        wait_time = 3 * (2 ** retry)
                        logger.warning(f"Rate limited on {model}, waiting {wait_time}s (retry {retry + 1})")
                        await asyncio.sleep(wait_time)
                        continue

                    # Handle model errors - try next model
                    if response.status_code in [404, 401, 403]:
                        logger.warning(f"Model {model} error {response.status_code}, trying next model")
                        break  # Break retry loop, go to next model

                    response.raise_for_status()
                    response_data = response.json()

                    if "choices" not in response_data or not response_data["choices"]:
                        logger.error(f"Invalid response from {model}, trying next model")
                        break

                    content = response_data["choices"][0]["message"]["content"]
                    if content:
                        logger.info(f"✅ Successfully used model: {model}")
                        return content
                    
                except httpx.TimeoutException:
                    logger.warning(f"Timeout with {model} (retry {retry + 1})")
                    if retry == max_retries_per_model - 1:
                        break  # Try next model
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error with {model}: {str(e)}")
                    if retry == max_retries_per_model - 1:
                        break  # Try next model
                    await asyncio.sleep(1)
        
        # All models failed, use demo fallback
        logger.warning("All OpenRouter models failed, using demo fallback")
        return self._get_demo_openrouter_response(prompt)

    def _get_demo_groq_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "photosynthesis" in prompt_lower:
            return "Photosynthesis is the process..."
        elif "machine learning" in prompt_lower:
            return "Machine Learning (ML) is a subset of..."
        else:
            return "I'm an AI tutor ready to help with academic subjects..."

    def _get_demo_openrouter_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()

        if "reverse" in prompt_lower and "string" in prompt_lower:
            return '''Here's how to reverse a string in Python:

```python
def reverse_string(s):
    return s[::-1]

# Example usage:
text = "Hello World"
print(reverse_string(text))  # "dlroW olleH"
```

**Time Complexity:** O(n)
**Best Practice:** Use slicing for simplicity'''
        elif "sort" in prompt_lower:
            return '''Here's how to sort a list in Python:

```python
def sort_list_builtin(lst):
    return sorted(lst)

numbers = [5, 3, 8, 1]
print(sort_list_builtin(numbers))  # [1, 3, 5, 8]
```'''
        else:
            return '''I'm your coding tutor! 💻

**Languages:** Python, Java, JavaScript  
**Concepts:** Data Structures, OOP, Algorithms  
What programming challenge can I help you solve?'''

    def __del__(self):
        if hasattr(self, "_http_client") and self._http_client and not self._http_client.is_closed:
            try:
                asyncio.create_task(self._http_client.aclose())
            except Exception:
                pass
