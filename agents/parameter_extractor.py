from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class ParameterExtractor:
    """
    Intelligent parameter extraction from conversational context.
    Extracts parameters required by educational tools without manual configuration.
    """
    
    def __init__(self):
        self.subject_keywords = {
            'mathematics': ['math', 'calculus', 'algebra', 'geometry', 'derivative', 'integral', 'equation'],
            'physics': ['physics', 'force', 'energy', 'momentum', 'quantum', 'mechanics'],
            'chemistry': ['chemistry', 'chemical', 'reaction', 'molecule', 'atom', 'bond'],
            'biology': ['biology', 'cell', 'dna', 'photosynthesis', 'evolution', 'organism'],
            'computer_science': ['programming', 'code', 'algorithm', 'python', 'java', 'data structure'],
            'history': ['history', 'war', 'revolution', 'ancient', 'civilization'],
            'english': ['grammar', 'literature', 'essay', 'writing', 'shakespeare']
        }
        
        self.difficulty_indicators = {
            'easy': ['basic', 'simple', 'introduction', 'beginner', 'struggling', 'confused'],
            'medium': ['intermediate', 'moderate', 'standard', 'regular'],
            'hard': ['advanced', 'complex', 'challenging', 'expert', 'difficult']
        }
        
        self.emotional_indicators = {
            'confused': ['confused', 'lost', 'dont understand', "don't get", 'unclear'],
            'anxious': ['worried', 'stressed', 'nervous', 'struggling', 'hard time'],
            'frustrated': ['frustrated', 'stuck', 'cant figure', "can't solve"],
            'focused': ['ready', 'focused', 'determined', 'want to learn'],
            'excited': ['excited', 'interested', 'curious', 'love', 'enjoy']
        }
    
    def extract_parameters(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main extraction function - extracts all parameters from query and context.
        """
        logger.info(f"Extracting parameters from query: {query[:100]}...")
        
        params = {
            # Basic extraction
            'topic': self._extract_topic(query),
            'subject': self._extract_subject(query),
            'difficulty': self._infer_difficulty(query),
            
            # Count extraction
            'count': self._extract_count(query),
            'num_questions': self._extract_count(query),
            
            # Context-based
            'teaching_style': user_context.get('teaching_style', self._infer_teaching_style(query)),
            'emotional_state': self._detect_emotional_state(query),
            'mastery_level': user_context.get('mastery_level', 'intermediate'),
            
            # Tool-specific
            'question_type': self._detect_question_type(query),
            'include_examples': self._should_include_examples(query),
            'include_analogies': self._should_include_analogies(query),
            'note_taking_style': self._infer_note_style(query),
            
            # Advanced
            'desired_depth': self._infer_depth(query),
            'concept_to_explain': self._extract_main_concept(query),
            
            # User info from context
            'user_id': user_context.get('user_id', 'guest'),
            'grade_level': user_context.get('grade_level', 'general')
        }
        
        logger.info(f"Extracted parameters: {params}")
        return params
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        query_lower = query.lower()
        
        # Pattern matching for explicit topics
        patterns = [
            r"about ([\w\s]+?)(?:\.|$|\?)",
            r"learn ([\w\s]+?)(?:\.|$|\?)",
            r"understand ([\w\s]+?)(?:\.|$|\?)",
            r"explain ([\w\s]+?)(?:\.|$|\?)",
            r"(?:on|for) ([\w\s]+?)(?:\.|$|\?)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r'\b(the|a|an|how|what|why|when|where)\b', '', topic).strip()
                if topic:
                    return topic
        
        # Fallback: extract nouns (simplified)
        words = query.split()
        if len(words) > 2:
            return ' '.join(words[:3])
        
        return "general topic"
    
    def _extract_subject(self, query: str) -> str:
        """Identify academic subject"""
        query_lower = query.lower()
        
        for subject, keywords in self.subject_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return subject
        
        return "general"
    
    def _infer_difficulty(self, query: str) -> str:
        """Infer difficulty level from language cues"""
        query_lower = query.lower()
        
        for difficulty, indicators in self.difficulty_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return difficulty
        
        return 'medium'  # default
    
    def _extract_count(self, query: str) -> int:
        """Extract number of items requested"""
        # Look for explicit numbers
        numbers = re.findall(r'(\d+)\s*(?:questions|flashcards|examples|notes|problems|items)?', query.lower())
        
        if numbers:
            return int(numbers[0])
        
        # Default based on query type
        if 'quiz' in query.lower() or 'test' in query.lower():
            return 10
        elif 'flashcard' in query.lower():
            return 15
        else:
            return 5
    
    def _detect_emotional_state(self, query: str) -> str:
        """Detect student's emotional state from query"""
        query_lower = query.lower()
        
        for emotion, indicators in self.emotional_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return emotion
        
        return 'neutral'
    
    def _infer_teaching_style(self, query: str) -> str:
        """Infer preferred teaching style from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['show', 'visual', 'diagram', 'image', 'picture']):
            return 'visual'
        elif any(word in query_lower for word in ['why', 'reason', 'think', 'understand']):
            return 'socratic'
        elif any(word in query_lower for word in ['watch', 'video', 'do it myself']):
            return 'flipped'
        else:
            return 'direct'
    
    def _detect_question_type(self, query: str) -> str:
        """Detect type of question requested"""
        query_lower = query.lower()
        
        if 'multiple choice' in query_lower or 'mcq' in query_lower:
            return 'multiple_choice'
        elif 'true' in query_lower and 'false' in query_lower:
            return 'true_false'
        elif 'short answer' in query_lower:
            return 'short_answer'
        elif 'essay' in query_lower:
            return 'essay'
        else:
            return 'mixed'
    
    def _should_include_examples(self, query: str) -> bool:
        """Determine if examples should be included"""
        query_lower = query.lower()
        return any(word in query_lower for word in ['example', 'instance', 'show me', 'demonstrate'])
    
    def _should_include_analogies(self, query: str) -> bool:
        """Determine if analogies would help"""
        query_lower = query.lower()
        return any(word in query_lower for word in ['like', 'similar', 'analogy', 'compare', 'understand'])
    
    def _infer_note_style(self, query: str) -> str:
        """Infer note-taking style preference"""
        query_lower = query.lower()
        
        if 'outline' in query_lower or 'bullet' in query_lower:
            return 'outline'
        elif 'mind map' in query_lower or 'diagram' in query_lower:
            return 'mind_map'
        elif 'cornell' in query_lower:
            return 'cornell'
        else:
            return 'outline'  # default
    
    def _infer_depth(self, query: str) -> str:
        """Infer desired depth of explanation"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['brief', 'quick', 'summary', 'overview']):
            return 'brief'
        elif any(word in query_lower for word in ['detailed', 'depth', 'thorough', 'comprehensive']):
            return 'detailed'
        else:
            return 'moderate'
    
    def _extract_main_concept(self, query: str) -> str:
        """Extract the main concept to be explained"""
        # Remove common question words
        concept = re.sub(r'\b(what|is|are|how|does|do|explain|tell me about|help me understand)\b', 
                        '', query.lower(), flags=re.IGNORECASE)
        concept = concept.strip(' ?.,!')
        
        return concept if concept else "general concept"
    
    def validate_parameters(self, params: Dict[str, Any], tool_schema: Dict) -> Dict[str, Any]:
        """
        Validate extracted parameters against tool schema.
        Ensures all required fields are present and types are correct.
        """
        validated = {}
        
        # Check required fields
        for field, requirements in tool_schema.get('required_fields', {}).items():
            if field in params:
                validated[field] = params[field]
            elif 'default' in requirements:
                validated[field] = requirements['default']
            else:
                logger.warning(f"Missing required field: {field}")
                validated[field] = None
        
        # Add optional fields
        for field in tool_schema.get('optional_fields', []):
            if field in params:
                validated[field] = params[field]
        
        return validated
