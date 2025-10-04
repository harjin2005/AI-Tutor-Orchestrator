# AI Tutor Orchestrator - Hackathon Project

**Tech Stack:** FastAPI + LangGraph + LangChain + SQLite + Groq + OpenRouter

**Architecture:** Hybrid Agent System (Approach 4) with specialized agents coordinated through workflows.

## API Keys Used:
- **Groq API:** For general tutoring (Mixtral model)
- **OpenRouter API:** For coding assistance (Agentica Deepcoder-14B)

## Structure:
- /agents - Agent implementations
- /tools - Utility tools
- /schemas - Database schemas
- /utils - Routes and utilities
- /tests - Test files

## Setup:
1. Ensure Docker is running
2. Run: docker compose up --build
3. API will be available at http://localhost:8000

## Endpoints:
- GET / - Health check
- POST /api/v1/ask?query=your_question - Ask the tutor
- GET /api/v1/history - Get recent interactions

## Free Stack:
- SQLite (no external DB needed)
- Groq API (free tier)
- OpenRouter free model
