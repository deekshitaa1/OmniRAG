from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse


router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
):
    workspace = Workspace(
        name=payload.name,
        description=payload.description,
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


@router.get(
    "",
    response_model=list[WorkspaceResponse],
)
def list_workspaces(
    db: Session = Depends(get_db),
):
    statement = select(Workspace).order_by(
        Workspace.created_at.desc()
    )

    return db.scalars(statement).all()


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    workspace = db.get(Workspace, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    return workspace
