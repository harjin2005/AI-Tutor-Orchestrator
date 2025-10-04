from .base_agent import BaseAgent
from typing import Dict, Any

class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_type = "tutor"
    
    async def process(self, query: str) -> Dict[str, Any]:
        # Use OpenRouter for coding questions
        if any(keyword in query.lower() for keyword in ["code", "programming", "function", "class"]):
            coding_prompt = f"As an expert coding tutor, help with this programming question: {query}"
            response = await self.call_openrouter(coding_prompt)
            return {
                "agent": self.agent_type,
                "response": response,
                "model_used": "openrouter_deepcoder"
            }
        
        # Use Groq for general tutoring
        else:
            tutor_prompt = f"As an AI tutor, provide a clear explanation for: {query}"
            response = await self.call_groq(tutor_prompt)
            return {
                "agent": self.agent_type,
                "response": response,
                "model_used": "groq_mixtral"
            }
