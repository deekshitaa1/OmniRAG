import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import (
    Document,
    DocumentSourceType,
    DocumentStatus,
)
from app.models.workspace import Workspace
from app.schemas.document import DocumentResponse
from app.services.ingestion.pipeline import ingest_document


router = APIRouter(
    prefix="/workspaces/{workspace_id}/documents",
    tags=["Documents"],
)


STORAGE_ROOT = Path("storage/documents")

ALLOWED_EXTENSIONS = {
    ".pdf": DocumentSourceType.PDF,
    ".csv": DocumentSourceType.CSV,
}


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Verify workspace exists
    workspace = db.get(Workspace, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Currently supported: PDF and CSV",
        )

    source_type = ALLOWED_EXTENSIONS[extension]

    # Read uploaded file
    content = file.file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    # Calculate SHA-256 checksum
    checksum = hashlib.sha256(content).hexdigest()

    # Detect duplicate
    existing = db.scalar(
        select(Document).where(
            Document.workspace_id == workspace_id,
            Document.checksum == checksum,
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This document already exists in the workspace",
        )

    # Generate document ID
    document_id = uuid.uuid4()

    # Create workspace storage directory
    workspace_directory = STORAGE_ROOT / str(workspace_id)
    workspace_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Store original file
    storage_path = workspace_directory / f"{document_id}{extension}"
    storage_path.write_bytes(content)

    # Create database record
    document = Document(
        id=document_id,
        workspace_id=workspace_id,
        name=file.filename,
        source_type=source_type,
        mime_type=file.content_type,
        file_path=str(storage_path),
        file_size=len(content),
        checksum=checksum,
        status=DocumentStatus.UPLOADED,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document
@router.post(
    "/{document_id}/ingest",
    response_model=DocumentResponse,
)
def ingest_uploaded_document(
    workspace_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.workspace_id == workspace_id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    try:
        ingest_document(
            document=document,
            db=db,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {exc}",
        ) from exc

    return document
