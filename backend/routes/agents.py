# backend/routes/agents.py

from fastapi import APIRouter

router = APIRouter()

@router.get("status")
async def get_agent_status():
    return {
        "planner_bot": "online",
        "editor_bot": "online",
        "business_agent_v1": "connected"
    }

@router.post("ping")
async def ping_agent():
    return { "pong": True }