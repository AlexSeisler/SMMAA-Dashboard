from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@router.get("/contents")
async def github_contents(owner: str, repo: str, path: str):
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GitHub token not set in environment.")

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
