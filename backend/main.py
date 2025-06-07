from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import tasks, files, webhooks, agents, github  # ✅ include GitHub

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

    # Basic health check
    @app.get("/ping")
    def ping():
        return {"status": "ok"}

    # Mount route modules
    app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
    app.include_router(files.router, prefix="/files", tags=["Files"])
    app.include_router(webhooks.router, prefix="/webhook", tags=["Webhooks"])
    app.include_router(agents.router, prefix="/agents", tags=["Agents"])
    app.include_router(github.router, prefix="/github", tags=["GitHub"])  # ✅ add GitHub

    return app

app = create_app()
