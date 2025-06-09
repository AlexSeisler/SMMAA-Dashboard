from fastapi import APIRouter, HTTPException, Request, Query
from uuid import uuid4
from db import fetch_all, fetch_one, execute
from models import Task

router = APIRouter()

# Legacy support
@router.get("/")
async def list_tasks(client_id: str):
    query = "SELECT * FROM tasks WHERE client_id = $1 ORDER BY inserted_at DESC"
    return await fetch_all(query, client_id)

@router.post("/")
async def create_task_legacy(task: Task):
    task_id = str(uuid4())
    query = """
        INSERT INTO tasks (id, client_id, task, status, priority, due, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await execute(query, task_id, task.client_id, task.task, task.status, task.priority, task.due, task.created_by)
    return { "task_id": task_id, "status": "created" }

# OpenAPI spec-compliant
@router.post("/create")
async def create_task(task: dict):
    task_id = str(uuid4())
    query = """
        INSERT INTO tasks (id, client_id, created_by, title, description, status)
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    await execute(
        query,
        task_id,
        task["client_id"],
        task["created_by"],
        task.get("title"),
        task.get("content"),
        "queued"
    )
    return {"task_id": task_id, "status": "queued"}

@router.get("/status")
async def get_task_status(task_id: str = Query(...)):
    query = "SELECT id, status FROM tasks WHERE id = $1"
    result = await fetch_one(query, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": result["id"], "status": result["status"]}
