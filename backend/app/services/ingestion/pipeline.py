from pathlib import Path

from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.extractors.pdf import extract_pdf_text


def ingest_document(
    document: Document,
    db: Session,
) -> Document:
    """
    Ingest an uploaded document.

    PDF pipeline:

        PDF file
            ↓
        text extraction
            ↓
        text chunking
            ↓
        DocumentChunk records
            ↓
        PROCESSED
    """

    try:
        document.status = DocumentStatus.PROCESSING
        document.error_message = None

        db.commit()
        db.refresh(document)

        if not document.file_path:
            raise ValueError("Document file path is missing")

        file_path = Path(document.file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Document file not found: {file_path}"
            )

        if document.source_type.value != "pdf":
            raise ValueError(
                f"Unsupported ingestion type: "
                f"{document.source_type.value}"
            )

        # --------------------------------------------------
        # 1. Extract PDF text
        # --------------------------------------------------

        extracted = extract_pdf_text(str(file_path))

        pages = extracted.get("pages", [])

        text = "\n\n".join(
            page.get("text", "")
            for page in pages
            if page.get("text")
        )

        if not text.strip():
            raise ValueError(
                "No text could be extracted from the PDF"
            )

        # --------------------------------------------------
        # 2. Chunk document
        # --------------------------------------------------

        chunks = chunk_text(text)

        if not chunks:
            raise ValueError(
                "Document produced zero chunks"
            )

        # --------------------------------------------------
        # 3. Remove old chunks if reprocessing
        # --------------------------------------------------

        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete(
            synchronize_session=False
        )

        # --------------------------------------------------
        # 4. Store chunks
        # --------------------------------------------------

        for index, chunk in enumerate(chunks):

            chunk_value = (
                chunk.text
                if hasattr(chunk, "text")
                else str(chunk)
            )

            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                text=chunk_value,
                character_count=len(chunk_value),
            )

            db.add(db_chunk)

        # --------------------------------------------------
        # 5. Mark document processed
        # --------------------------------------------------

        document.status = DocumentStatus.PROCESSED
        document.error_message = None

        db.commit()
        db.refresh(document)

        return document

    except Exception as exc:

        db.rollback()

        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)

        db.add(document)
        db.commit()
        db.refresh(document)

        raise
