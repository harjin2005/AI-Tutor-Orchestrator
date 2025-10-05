from pydantic import BaseModel
from typing import Optional

class UserContext(BaseModel):
    user_id: str = "student123"
    name: str = "Demo Student"
    grade_level: str = "10"
    learning_style_summary: str = "Visual learner, prefers examples"
    emotional_state_summary: str = "Focused and motivated"
    mastery_level_summary: str = "Level 7: Proficient"
    teaching_style: str = "direct"  # direct, socratic, visual, flipped

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student123",
                "name": "Harry",
                "grade_level": "10",
                "learning_style_summary": "Prefers outlines and structured notes",
                "emotional_state_summary": "Relaxed and attentive",
                "mastery_level_summary": "Level 7: Proficient",
                "teaching_style": "visual"
            }
        }
