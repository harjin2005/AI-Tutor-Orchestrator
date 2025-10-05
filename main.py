from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import os
from utils.routes import router
from schemas.database import create_tables, test_database_connection

app = FastAPI(
    title="AI Tutor Orchestrator",
    description="Hackathon Project - Hybrid Agent System with LangGraph",
    version="1.0.0"
)

# Test database connection before starting
print("🧪 Testing database connection...")
if not test_database_connection():
    print("❌ Database connection failed. Check your DATABASE_URL.")
    print("💡 Tip: Run 'python test_db.py' for detailed connection testing.")
    exit(1)

# Create database tables
create_tables()

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "AI Tutor Orchestrator API is running",
        "database": "connected",
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "model": os.getenv("OPENROUTER_MODEL", "Not configured")
    }

@app.get("/health")
def health_check():
    db_url = os.getenv("DATABASE_URL", "Not set")
    db_type = "PostgreSQL" if db_url.startswith("postgresql") else "SQLite"
    return {"status": "healthy", "database": db_type}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
