import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    source_type: str
    mime_type: str | None
    file_size: int | None
    checksum: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
