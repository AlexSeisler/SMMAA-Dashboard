from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"
OWNER = "AlexSeisler"
REPO = "SMMAA-Dashboard"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

@router.get("/contents")
async def github_contents(
    path: str,
    owner: str = OWNER,
    repo: str = REPO,
    ref: str = "main"
):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/raw")
async def github_raw(
    path: str,
    owner: str = OWNER,
    repo: str = REPO,
    ref: str = "main"
):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.text

@router.get("/list")
async def github_list(
    path: str = "",
    owner: str = OWNER,
    repo: str = REPO,
    ref: str = "main"
):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/tree")
async def github_tree(
    owner: str = OWNER,
    repo: str = REPO,
    ref: str = "main"
):
    # First get the SHA of the tree at the specified ref
    branch_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{ref}"
    async with httpx.AsyncClient() as client:
        ref_response = await client.get(branch_url, headers=HEADERS)
        if ref_response.status_code != 200:
            raise HTTPException(status_code=ref_response.status_code, detail=ref_response.text)

        sha = ref_response.json()["object"]["sha"]
        commit_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits/{sha}"
        commit_response = await client.get(commit_url, headers=HEADERS)
        tree_sha = commit_response.json()["tree"]["sha"]

        # Get the full recursive tree
        tree_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"
        tree_response = await client.get(tree_url, headers=HEADERS)
        if tree_response.status_code != 200:
            raise HTTPException(status_code=tree_response.status_code, detail=tree_response.text)

        return tree_response.json()
