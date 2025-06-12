# backend/routes/github.py

import os
import requests
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

GITHUB_API = "https://api.github.com"
OWNER = os.getenv("GITHUB_OWNER", "AlexSeisler")
REPO = os.getenv("GITHUB_REPO", "SMMAA-Dashboard")
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


# Health check route
@router.get("/health")
async def github_health():
    return {"github_status": "connected", "owner": OWNER, "repo": REPO}


# ✅ Existing route (keep for backwards compatibility)
@router.get("/tree")
async def github_tree(owner: str = OWNER, repo: str = REPO, ref: str = "main", recursive: int = 1):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{ref}?recursive={recursive}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


# ✅ New Dev Agent Friendly Route — supports both agents + scanner loops
@router.get("/repo/tree")
async def github_repo_tree(
    owner: str = OWNER,
    repo: str = REPO,
    branch: str = "main",
    recursive: bool = Query(True)

):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive={recursive}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


# ✅ Repo status
@router.get("/repo/status")
async def github_repo_status(owner: str = OWNER, repo: str = REPO):
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


# ✅ Raw file fetch
@router.get("/repo/file")
async def github_file_raw(owner: str = OWNER, repo: str = REPO, path: str = "", branch: str = "main"):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    content = response.json()
    return {
        "path": content.get("path"),
        "size": content.get("size"),
        "encoding": content.get("encoding"),
        "content": content.get("content"),
    }