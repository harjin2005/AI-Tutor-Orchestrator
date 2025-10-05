from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas.database import get_db, AgentInteraction
from agents.tutor_agent import TutorAgent
from agents.langgraph_agent import LangGraphTutorAgent
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "true").lower() == "true"

# Request Models
class TutorQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="The question or query for the AI tutor")
    model_config = ConfigDict(
        json_schema_extra={"example": {"query": "Generate 7 flashcards for photosynthesis. Visual examples please."}}
    )

# Response Model
class TutorResponse(BaseModel):
    agent: str
    response: str
    model_used: str
    selected_tool: Optional[str] = None
    extracted_params: Optional[dict] = None
    tool_result: Optional[dict] = None
    classification: Optional[str] = None
    confidence: Optional[str] = None
    timestamp: datetime
    architecture: Optional[str] = None
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "agent": "tutor_langgraph",
                "response": "Flashcards generated.",
                "model_used": "none",
                "selected_tool": "flashcard",
                "extracted_params": {"topic": "photosynthesis", "count": 7, "teaching_style": "visual"},
                "tool_result": {"flashcards": [...]},
                "classification": "academic",
                "confidence": "high",
                "timestamp": "2025-10-05T08:30:00Z",
                "architecture": "langgraph"
            }
        }
    )

class HistoryItem(BaseModel):
    query: str
    response: str
    agent: str
    created_at: datetime
    classification: Optional[str] = None

class HistoryResponse(BaseModel):
    interactions: List[HistoryItem]
    total_count: int
    architecture: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime

def get_agent():
    # ADDED: Print + log debug info
    print("(DEBUG) USE_LANGGRAPH =", USE_LANGGRAPH)
    logger.info(f"(DEBUG) USE_LANGGRAPH={USE_LANGGRAPH}")
    if USE_LANGGRAPH:
        try:
            print("Trying LangGraph agent...")
            agent = LangGraphTutorAgent()  # This is where failure occurs if imports/config broken
            print("LangGraph agent loaded!")
            logger.info("✅ Using LangGraph StateGraph agent")
            return agent, "langgraph"
        except Exception as e:
            print(f"(DEBUG) LangGraph error: {e}")
            logger.warning(f"⚠️ LangGraph initialization failed: {e}. Falling back to standard agent.")
            agent = TutorAgent()
            return agent, "standard"
    else:
        print("Using standard agent!")
        logger.info("✅ Using standard agent")
        agent = TutorAgent()
        return agent, "standard"

@router.post("/ask", response_model=TutorResponse, status_code=status.HTTP_200_OK)
async def ask_tutor(request: TutorQueryRequest, db: Session = Depends(get_db)):
    tutor = None
    architecture = "unknown"
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        tutor, architecture = get_agent()
        logger.info(f"Processing query with {architecture} architecture: {request.query[:100]}...")
        print("(DEBUG) Ask requested with architecture:", architecture)
        result = await tutor.process(request.query)
        if "error" in result:
            logger.error(f"Agent processing error: {result['error']}")
            print("(DEBUG) Agent processing error:", result['error'])
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing your request. Please try again."
            )
        try:
            interaction = AgentInteraction(
                agent_type=result["agent"],
                user_query=request.query,
                agent_response=result["response"],
                model_used=result.get("model_used"),
                classification=result.get("selected_tool") or result.get("classification"),
                confidence=result.get("confidence", "high")
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            timestamp = interaction.created_at
        except Exception as e:
            logger.warning(f"DB save failed: {e}")
            print("(DEBUG) DB save failed:", e)
            timestamp = datetime.utcnow()
        return TutorResponse(
            agent=result.get("agent", ""),
            response=result.get("response", ""),
            model_used=result.get("model_used", ""),
            selected_tool=result.get("selected_tool"),
            extracted_params=result.get("extracted_params"),
            tool_result=result.get("tool_result"),
            classification=result.get("classification"),
            confidence=result.get("confidence", "high"),
            timestamp=timestamp,
            architecture=architecture
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ask_tutor: {str(e)}", exc_info=True)
        print("(DEBUG) Unexpected error in ask_tutor:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
    finally:
        if tutor and hasattr(tutor, 'close_http_client'):
            try:
                await tutor.close_http_client()
            except Exception as cleanup_error:
                logger.warning(f"Error closing HTTP client: {cleanup_error}")
                print("(DEBUG) Error closing HTTP client:", cleanup_error)

@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
async def get_history(
    limit: int = Query(default=10, ge=1, le=100, description="Number of interactions to retrieve"),
    offset: int = Query(default=0, ge=0, description="Number of interactions to skip"),
    db: Session = Depends(get_db)
):
    try:
        total_count = db.query(AgentInteraction).count()
        interactions = (
            db.query(AgentInteraction)
            .order_by(AgentInteraction.created_at.desc())
            .offset(offset).limit(limit).all()
        )
        history_items = [
            HistoryItem(
                query=interaction.user_query,
                response=interaction.agent_response,
                agent=interaction.agent_type,
                created_at=interaction.created_at,
                classification=interaction.classification
            )
            for interaction in interactions
        ]
        _, current_architecture = get_agent()
        return HistoryResponse(
            interactions=history_items,
            total_count=total_count,
            architecture=current_architecture
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_history: {str(e)}")
        print("(DEBUG) Database error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history"
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_history: {str(e)}")
        print("(DEBUG) Unexpected error in get_history:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/architecture", status_code=status.HTTP_200_OK)
async def get_architecture_info():
    try:
        _, architecture = get_agent()
        print("(DEBUG) /architecture endpoint:", architecture)
        return {
            "architecture": architecture,
            "use_langgraph": USE_LANGGRAPH,
            "description": (
                "LangGraph StateGraph with conditional routing" 
                if architecture == "langgraph" 
                else "Standard agent with direct routing"
            ),
            "features": {
                "state_management": architecture == "langgraph",
                "graph_visualization": architecture == "langgraph",
                "conditional_edges": architecture == "langgraph",
                "fallback_support": True,
                "multi_model_routing": True
            },
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting architecture info: {str(e)}")
        print("(DEBUG) Error getting architecture info:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving architecture information"
        )

@router.get("/health", status_code=status.HTTP_200_OK)
async def router_health():
    try:
        _, architecture = get_agent()
        print("(DEBUG) /health:", architecture)
        return {
            "status": "healthy",
            "router": "tutor_api",
            "architecture": architecture,
            "langgraph_enabled": USE_LANGGRAPH,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.warning(f"Health check partial failure: {e}")
        print("(DEBUG) Health check partial failure:", e)
        return {
            "status": "degraded",
            "router": "tutor_api",
            "error": str(e),
            "timestamp": datetime.now()
        }
