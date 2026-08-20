from fastapi import FastAPI

from app.api.routes.documents import router as document_router
from app.api.routes.workspaces import router as workspace_router


app = FastAPI(
    title="OmniRAG",
    version="0.1.0",
    description="Enterprise AI Knowledge Platform",
)


app.include_router(workspace_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "name": "OmniRAG",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
