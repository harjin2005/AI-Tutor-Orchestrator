from .base_agent import BaseAgent
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_type = "tutor"
        
        # Enhanced keyword sets for better classification
        self.coding_keywords = [
            # Programming languages
            "python", "javascript", "java", "c++", "html", "css", "react", "node",
            # Programming concepts
            "code", "coding", "programming", "function", "class", "variable", "loop",
            "algorithm", "data structure", "array", "object", "method", "debug",
            # Technical terms
            "api", "database", "sql", "git", "framework", "library", "syntax",
            "compile", "runtime", "exception", "import", "export", "async"
        ]
        
        self.academic_keywords = [
            "math", "mathematics", "physics", "chemistry", "biology", "history",
            "literature", "science", "equation", "formula", "theorem", "concept",
            "study", "learn", "understand", "explain", "calculate", "solve"
        ]
    
    async def process(self, query: str) -> Dict[str, Any]:
        try:
            # Enhanced query classification
            classification = self._classify_query(query)
            
            if classification == "coding":
                coding_prompt = self._build_coding_prompt(query)
                response = await self.call_openrouter(coding_prompt)
                return {
                    "agent": self.agent_type,
                    "response": response,
                    "model_used": "openrouter_deepcoder",
                    "classification": "coding",
                    "confidence": "high"
                }
            
            elif classification == "academic":
                academic_prompt = self._build_academic_prompt(query)
                response = await self.call_groq(academic_prompt)
                return {
                    "agent": self.agent_type,
                    "response": response,
                    "model_used": "groq_mixtral",
                    "classification": "academic",
                    "confidence": "high"
                }
            
            else:  # General tutoring
                general_prompt = self._build_general_prompt(query)
                response = await self.call_groq(general_prompt)
                return {
                    "agent": self.agent_type,
                    "response": response,
                    "model_used": "groq_mixtral",
                    "classification": "general",
                    "confidence": "medium"
                }
                
        except Exception as e:
            logger.error(f"Error in TutorAgent.process: {str(e)}")
            return {
                "agent": self.agent_type,
                "response": "I apologize, but I encountered an error. Please try rephrasing your question.",
                "model_used": "error",
                "error": str(e)
            }
    
    def _classify_query(self, query: str) -> str:
        """Enhanced query classification with better accuracy"""
        query_lower = query.lower()
        
        # Check for coding-related content
        coding_score = sum(1 for keyword in self.coding_keywords if keyword in query_lower)
        
        # Check for academic subjects
        academic_score = sum(1 for keyword in self.academic_keywords if keyword in query_lower)
        
        # Look for code patterns
        has_code_patterns = bool(
            re.search(r'[\{\}\[\];]', query) or  # Code syntax
            re.search(r'def |function |class |import |from ', query_lower) or  # Keywords
            re.search(r'\.py|\.js|\.java|\.cpp', query_lower)  # File extensions
        )
        
        if coding_score >= 2 or has_code_patterns:
            return "coding"
        elif academic_score >= 1:
            return "academic"
        else:
            return "general"
    
    def _build_coding_prompt(self, query: str) -> str:
        """Build specialized prompt for coding questions"""
        return f"""You are an expert programming tutor with deep knowledge in multiple programming languages and software development best practices.

User's coding question: {query}

Please provide:
1. A clear, step-by-step explanation
2. Working code examples when applicable
3. Best practices and common pitfalls
4. Alternative approaches if relevant

Focus on being educational and helping the user understand concepts, not just providing solutions."""

    def _build_academic_prompt(self, query: str) -> str:
        """Build specialized prompt for academic subjects"""
        return f"""You are an experienced academic tutor skilled in explaining complex concepts in simple, understandable terms.

Student's question: {query}

Please provide:
1. A clear explanation of the concept
2. Real-world examples or analogies
3. Step-by-step problem solving if applicable
4. Key points to remember

Make your explanation accessible and engaging for learning."""

    def _build_general_prompt(self, query: str) -> str:
        """Build prompt for general tutoring questions"""
        return f"""You are a helpful AI tutor dedicated to supporting student learning across various subjects.

Student's question: {query}

Please provide a clear, helpful response that:
1. Addresses the question directly
2. Provides context and background information
3. Suggests related topics for further learning
4. Encourages critical thinking

Be supportive and encouraging in your response."""
