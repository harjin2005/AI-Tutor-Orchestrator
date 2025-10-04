from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.database import get_db, AgentInteraction
from agents import TutorAgent

router = APIRouter()

@router.post("/ask")
async def ask_tutor(query: str, db: Session = Depends(get_db)):
    tutor = TutorAgent()
    result = await tutor.process(query)
    
    # Save interaction to database
    interaction = AgentInteraction(
        agent_type=result["agent"],
        user_query=query,
        agent_response=result["response"]
    )
    db.add(interaction)
    db.commit()
    
    return result

@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    interactions = db.query(AgentInteraction).order_by(AgentInteraction.created_at.desc()).limit(10).all()
    return [{"query": i.user_query, "response": i.agent_response, "agent": i.agent_type} for i in interactions]
