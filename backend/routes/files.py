# backend/routes/files.py

from fastapi import APIRouter, HTTPException, Request
from db import fetch_all, execute
from models import File
from uuid import uuid4

router = APIRouter()

# GET /files?client_id=...&task_id=...
@router.get("/")
async def list_files(client_id: str, task_id: str = None):
    if task_id:
        query = "SELECT * FROM files WHERE client_id = $1 AND task_id = $2 ORDER BY inserted_at DESC"
        return await fetch_all(query, client_id, task_id)
    else:
        query = "SELECT * FROM files WHERE client_id = $1 ORDER BY inserted_at DESC"
        return await fetch_all(query, client_id)

# POST /files
@router.post("/")
async def add_file(file: File):
    file_id = str(uuid4())
    query = """
        INSERT INTO files (id, task_id, client_id, file_url, status)
        VALUES ($1, $2, $3, $4, $5)
    """
    await execute(query, file_id, file.task_id, file.client_id, file.file_url, file.status)
    return { "file_id": file_id, "status": "uploaded" }
