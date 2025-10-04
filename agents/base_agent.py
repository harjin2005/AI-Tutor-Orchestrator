from abc import ABC, abstractmethod
from typing import Dict, Any
import os
from groq import Groq
import httpx

class BaseAgent(ABC):
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL")
    
    @abstractmethod
    async def process(self, query: str) -> Dict[str, Any]:
        pass
    
    async def call_groq(self, prompt: str, model: str = "mixtral-8x7b-32768"):
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Groq Error: {str(e)}"
    
    async def call_openrouter(self, prompt: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.openrouter_model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"OpenRouter Error: {str(e)}"
