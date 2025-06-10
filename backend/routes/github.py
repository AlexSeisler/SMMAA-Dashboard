from fastapi import APIRouter, HTTPException, Body
import httpx
import os

router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
GITHUB_API_BASE = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# --------------------- Raw / List / Tree ---------------------
@router.get("/contents")
async def github_contents(path: str, owner: str = OWNER, repo: str = REPO, ref: str = "main"):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/raw")
async def github_raw(path: str, owner: str = OWNER, repo: str = REPO, ref: str = "main"):
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.text

@router.get("/list")
async def github_list(path: str = "", owner: str = OWNER, repo: str = REPO, ref: str = "main"):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

@router.get("/tree")
async def github_tree(owner: str = OWNER, repo: str = REPO, ref: str = "main"):
    async with httpx.AsyncClient() as client:
        ref_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{ref}", headers=HEADERS)
        if ref_res.status_code != 200:
            raise HTTPException(status_code=ref_res.status_code, detail=ref_res.text)
        commit_sha = ref_res.json()["object"]["sha"]
        commit_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits/{commit_sha}", headers=HEADERS)
        tree_sha = commit_res.json()["tree"]["sha"]
        tree_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1", headers=HEADERS)
        if tree_res.status_code != 200:
            raise HTTPException(status_code=tree_res.status_code, detail=tree_res.text)
        return tree_res.json()

# --------------------- Commits ---------------------
@router.post("/repo/commit")
async def commit_to_repo(
    owner: str = Body(...),
    repo: str = Body(...),
    message: str = Body(...),
    branch: str = Body(...),
    files: list = Body(...),
    create_pull_request: bool = Body(False),
    agent_id: str = Body(None),
    task_id: str = Body(None)
):
    async with httpx.AsyncClient() as client:
        # Step 1: Get latest commit SHA on branch
        ref_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/ref/heads/{branch}"
        ref_res = await client.get(ref_url, headers=HEADERS)
        if ref_res.status_code != 200:
            raise HTTPException(status_code=ref_res.status_code, detail=ref_res.text)
        latest_commit_sha = ref_res.json()["object"]["sha"]

        # Step 2: Get base tree SHA
        commit_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits/{latest_commit_sha}"
        commit_res = await client.get(commit_url, headers=HEADERS)
        base_tree_sha = commit_res.json()["tree"]["sha"]

        # Step 3: Create new blobs for each file
        blob_shas = []
        for f in files:
            blob_res = await client.post(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/blobs",
                headers=HEADERS,
                json={"content": f["content"], "encoding": "utf-8"}
            )
            blob_shas.append({
                "path": f["path"],
                "mode": "100644",
                "type": "blob",
                "sha": blob_res.json()["sha"]
            })

        # Step 4: Create new tree
        tree_res = await client.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees",
            headers=HEADERS,
            json={"base_tree": base_tree_sha, "tree": blob_shas}
        )
        new_tree_sha = tree_res.json()["sha"]

        # Step 5: Create commit
        commit_payload = {
            "message": message,
            "tree": new_tree_sha,
            "parents": [latest_commit_sha]
        }
        commit_res = await client.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/commits",
            headers=HEADERS,
            json=commit_payload
        )
        new_commit_sha = commit_res.json()["sha"]

        # Step 6: Update ref
        update_res = await client.patch(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{branch}",
            headers=HEADERS,
            json={"sha": new_commit_sha}
        )

        return {"commit": new_commit_sha, "status": "committed", "files": [f["path"] for f in files]}

# --------------------- Branch ---------------------
@router.post("/repo/branch")
async def create_branch(owner: str = OWNER, repo: str = REPO, new_branch: str = Body(...), base_branch: str = Body(...)):
    async with httpx.AsyncClient() as client:
        ref_res = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs/heads/{base_branch}", headers=HEADERS)
        if ref_res.status_code != 200:
            raise HTTPException(status_code=ref_res.status_code, detail=ref_res.text)
        sha = ref_res.json()["object"]["sha"]
        branch_payload = {"ref": f"refs/heads/{new_branch}", "sha": sha}
        branch_res = await client.post(f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/refs", json=branch_payload, headers=HEADERS)
        return branch_res.json()

# --------------------- Init / Scaffold ---------------------
@router.post("/repo/init")
async def init_file_scaffold(owner: str = OWNER, repo: str = REPO, branch: str = Body(...), scaffold: list = Body(...)):
    message = "Init scaffold"
    return await commit_to_repo(
        owner=owner,
        repo=repo,
        message=message,
        branch=branch,
        files=scaffold,
        create_pull_request=False,
        agent_id=None,
        task_id=None
    )


# --------------------- Workflow ---------------------
@router.post("/repo/workflows/dispatch")
async def trigger_workflow(owner: str, repo: str, workflow_id: str, ref: str, inputs: dict = Body(default={})):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    payload = {"ref": ref, "inputs": inputs}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers=HEADERS)
        if res.status_code not in [204, 201]:
            raise HTTPException(status_code=res.status_code, detail=res.text)
        return {"status": "dispatched", "workflow": workflow_id}

# --------------------- Deployments ---------------------
@router.post("/repo/deployments")
async def create_deployment(owner: str, repo: str, ref: str, environment: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/deployments"
    payload = {"ref": ref, "environment": environment, "auto_merge": False, "required_contexts": []}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers=HEADERS)
        return res.json()

# --------------------- Webhooks ---------------------
@router.post("/repo/hooks")
async def create_webhook(owner: str, repo: str, config: dict, events: list):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/hooks"
    payload = {"config": config, "events": events}
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers=HEADERS)
        return res.json()

# --------------------- Repo Status ---------------------
@router.get("/repo/status")
async def get_repo_status(owner: str, repo: str):
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=HEADERS)
        return res.json()
