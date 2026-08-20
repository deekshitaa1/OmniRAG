from pathlib import Path

from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails."""


def extract_pdf_text(file_path: str | Path) -> dict:
    """
    Extract text from every page of a PDF.

    Returns:
        {
            "page_count": int,
            "pages": [
                {
                    "page_number": int,
                    "text": str,
                    "character_count": int
                }
            ],
            "total_characters": int
        }
    """

    path = Path(file_path)

    if not path.exists():
        raise PDFExtractionError(
            f"PDF file does not exist: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise PDFExtractionError(
            f"Expected PDF file, got: {path.suffix}"
        )

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise PDFExtractionError(
            f"Unable to read PDF: {exc}"
        ) from exc

    pages = []
    total_characters = 0

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            raise PDFExtractionError(
                f"Failed extracting page {page_number}: {exc}"
            ) from exc

        # Normalize whitespace while preserving paragraph boundaries.
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        clean_text = "\n".join(lines)

        character_count = len(clean_text)
        total_characters += character_count

        pages.append(
            {
                "page_number": page_number,
                "text": clean_text,
                "character_count": character_count,
            }
        )

    return {
        "page_count": len(reader.pages),
        "pages": pages,
        "total_characters": total_characters,
    }
