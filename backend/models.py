# backend/models.py

from pydantic import BaseModel
from typing import List, Optional

class Task(BaseModel):
    id: Optional[str]
    client_id: str
    task: str
    status: str = "to_do"
    priority: Optional[str] = "medium"
    due: Optional[str]
    created_by: Optional[str]

class File(BaseModel):
    id: Optional[str]
    task_id: str
    client_id: str
    file_url: str
    status: str = "uploaded"

class Client(BaseModel):
    id: str
    name: str
    status: Optional[str] = "active"
