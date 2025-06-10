from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db import init_db  # ✅ Add DB pool initializer
import os

load_dotenv()

from routes import tasks, files, webhooks, agents, github


def create_app():
    app = FastAPI(
        title="SMMAA Agent API",
        version="1.0.0",
        description="Agent-integrated task + file manager for SMMAA dashboard."
    )

    # Enable CORS for frontend dev server and hosting environments
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/ping")
    def ping():
        return {"status": "ok"}

    # On startup, initialize DB
    @app.on_event("startup")
    async def startup_event():
        source = "Render" if "RENDER" in os.environ else "Local"
        print(f"[DB INIT] Environment: {source}")
        await init_db()
    

    # Optional: shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        print("🛑 App is shutting down")

    # Route Mounts
    app.include_router(tasks.router, prefix="/task", tags=["Tasks"])
    app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
    app.include_router(files.router, prefix="/files", tags=["Files"])
    app.include_router(webhooks.router, prefix="/webhook", tags=["Webhooks"])
    app.include_router(agents.router, prefix="/agents", tags=["Agents"])
    app.include_router(github.router, prefix="/github", tags=["GitHub"])

    return app

app = create_app()
