# backend/routes/github.py

import os
import requests
import urllib.parse
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# GitHub API setup
GITHUB_API = "https://api.github.com"
OWNER = os.getenv("GITHUB_OWNER", "AlexSeisler")
REPO = os.getenv("GITHUB_REPO", "SMMAA-Dashboard")
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ✅ Health Check
@router.get("/health")
async def github_health():
    return {"github_status": "connected", "owner": OWNER, "repo": REPO}

# ✅ Repo Status
@router.get("/repo/status")
async def github_repo_status(owner: str = OWNER, repo: str = REPO):
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Repo Tree (recursive file listing)
@router.get("/repo/tree")
async def github_repo_tree(
    owner: str = OWNER,
    repo: str = REPO,
    branch: str = "main",
    recursive: bool = Query(True)
):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive={int(recursive)}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

# ✅ Raw file fetch
@router.get("/raw")
async def github_raw_file(
    path: str,
    owner: str = OWNER,
    repo: str = REPO,
    branch: str = "main"
):
    decoded_path = urllib.parse.unquote(path)
    encoded_path = urllib.parse.quote(decoded_path, safe="")

    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{encoded_path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    content = response.json()
    return {
        "path": content.get("path"),
        "size": content.get("size"),
        "encoding": content.get("encoding"),
        "content": content.get("content"),
        "download_url": content.get("download_url")
    }

# ✅ Commit to repo
@router.post("/repo/commit")
async def commit_to_repo(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    branch = payload.get("branch", "main")
    message = payload.get("message")
    files = payload.get("files", [])
    create_pr = payload.get("create_pull_request", False)

    # 1️⃣ Get latest commit SHA
    ref_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/refs/heads/{branch}"
    ref_response = requests.get(ref_url, headers=HEADERS)
    if ref_response.status_code != 200:
        raise HTTPException(status_code=ref_response.status_code, detail=ref_response.json())
    latest_commit_sha = ref_response.json()["object"]["sha"]

    # 2️⃣ Get tree SHA
    commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/commits/{latest_commit_sha}"
    commit_response = requests.get(commit_url, headers=HEADERS)
    if commit_response.status_code != 200:
        raise HTTPException(status_code=commit_response.status_code, detail=commit_response.json())
    base_tree_sha = commit_response.json()["tree"]["sha"]

    # 3️⃣ Create blobs for each file
    blobs = []
    for file in files:
        blob_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/blobs"
        blob_response = requests.post(blob_url, headers=HEADERS, json={
            "content": file["content"],
            "encoding": "utf-8"
        })
        if blob_response.status_code != 201:
            raise HTTPException(status_code=blob_response.status_code, detail=blob_response.json())
        blobs.append({
            "path": file["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_response.json()["sha"]
        })

    # 4️⃣ Create tree
    tree_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees"
    tree_response = requests.post(tree_url, headers=HEADERS, json={
        "base_tree": base_tree_sha,
        "tree": blobs
    })
    if tree_response.status_code != 201:
        raise HTTPException(status_code=tree_response.status_code, detail=tree_response.json())
    new_tree_sha = tree_response.json()["sha"]

    # 5️⃣ Create commit
    commit_create_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/commits"
    commit_create_response = requests.post(commit_create_url, headers=HEADERS, json={
        "message": message,
        "tree": new_tree_sha,
        "parents": [latest_commit_sha]
    })
    if commit_create_response.status_code != 201:
        raise HTTPException(status_code=commit_create_response.status_code, detail=commit_create_response.json())
    new_commit_sha = commit_create_response.json()["sha"]

    # 6️⃣ Update branch ref
    update_ref_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/refs/heads/{branch}"
    update_ref_response = requests.patch(update_ref_url, headers=HEADERS, json={
        "sha": new_commit_sha
    })
    if update_ref_response.status_code not in [200, 201]:
        raise HTTPException(status_code=update_ref_response.status_code, detail=update_ref_response.json())

    return {"status": "committed", "commit_sha": new_commit_sha}

# ✅ Delete file from repo
@router.delete("/repo/file")
async def delete_file_from_repo(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    path = payload.get("path")
    message = payload.get("message")
    sha = payload.get("sha")
    branch = payload.get("branch", "main")

    encoded_path = urllib.parse.quote(path, safe="")
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{encoded_path}"

    response = requests.delete(url, headers=HEADERS, json={
        "message": message,
        "sha": sha,
        "branch": branch
    })

    if response.status_code not in [200, 204]:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "deleted"}

# ✅ Create branch
@router.post("/repo/branch")
async def create_branch(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    new_branch = payload.get("new_branch")
    base_branch = payload.get("base_branch", "main")

    ref_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/refs/heads/{base_branch}"
    ref_response = requests.get(ref_url, headers=HEADERS)
    if ref_response.status_code != 200:
        raise HTTPException(status_code=ref_response.status_code, detail=ref_response.json())

    base_sha = ref_response.json()["object"]["sha"]

    create_ref_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/refs"
    response = requests.post(create_ref_url, headers=HEADERS, json={
        "ref": f"refs/heads/{new_branch}",
        "sha": base_sha
    })

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "branch_created", "branch": new_branch}

# ✅ Init scaffold
@router.post("/repo/init")
async def init_file_scaffold(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    branch = payload.get("branch", "main")
    scaffold = payload.get("scaffold", [])

    files_payload = []
    for file in scaffold:
        files_payload.append({
            "path": file["path"],
            "content": file["content"]
        })

    commit_payload = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "message": "Initial scaffold",
        "files": files_payload
    }

    return await commit_to_repo(commit_payload)

# ✅ Create Webhook
@router.post("/repo/hooks")
async def create_webhook(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    config = payload.get("config", {})
    events = payload.get("events", [])

    url = f"{GITHUB_API}/repos/{owner}/{repo}/hooks"
    response = requests.post(url, headers=HEADERS, json={
        "config": config,
        "events": events
    })

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "webhook_created"}

# ✅ Create Deployment
@router.post("/repo/deployments")
async def create_deployment(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    ref = payload.get("ref")
    environment = payload.get("environment", "production")

    url = f"{GITHUB_API}/repos/{owner}/{repo}/deployments"
    response = requests.post(url, headers=HEADERS, json={
        "ref": ref,
        "environment": environment
    })

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "deployment_created"}

# ✅ Trigger Workflow
@router.post("/repo/workflows/dispatch")
async def trigger_workflow(payload: dict):
    owner = payload.get("owner", OWNER)
    repo = payload.get("repo", REPO)
    workflow_id = payload.get("workflow_id")
    ref = payload.get("ref", "main")
    inputs = payload.get("inputs", {})

    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    response = requests.post(url, headers=HEADERS, json={
        "ref": ref,
        "inputs": inputs
    })

    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return {"status": "workflow_triggered"}