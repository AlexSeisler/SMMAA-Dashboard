# backend/routes/tasks.py

from fastapi import APIRouter, HTTPException, Request
from db import fetch_all, fetch_one, execute
from models import Task
from uuid import uuid4

router = APIRouter()

# GET /tasks?client_id=...
@router.get("/")
async def list_tasks(client_id: str):
    query = "SELECT * FROM tasks WHERE client_id = $1 ORDER BY inserted_at DESC"
    return await fetch_all(query, client_id)

# POST /tasks
@router.post("/")
async def create_task(task: Task):
    task_id = str(uuid4())
    query = """
        INSERT INTO tasks (id, client_id, task, status, priority, due, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await execute(query, task_id, task.client_id, task.task, task.status, task.priority, task.due, task.created_by)
    return { "task_id": task_id, "status": "created" }
