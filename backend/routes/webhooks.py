# backend/routes/webhooks.py

from fastapi import APIRouter, Request, HTTPException
from uuid import uuid4
from db import execute

router = APIRouter()

@router.post("/")
async def receive_webhook(request: Request):
    payload = await request.json()
    
    client_id = payload.get("client_id")
    source = payload.get("source", "unknown")

    if not client_id or not payload.get("task"):
        raise HTTPException(status_code=400, detail="Invalid payload")

    task_id = str(uuid4())

    query = """
        INSERT INTO tasks (id, client_id, task, status, priority, due, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await execute(
        query,
        task_id,
        client_id,
        payload["task"],
        payload.get("status", "to_do"),
        payload.get("priority", "medium"),
        payload.get("due"),
        source
    )

    return { "received": True, "task_id": task_id }
