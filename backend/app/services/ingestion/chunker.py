from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    text: str
    character_count: int


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:
    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    # Normalize only the complete document once.
    text = text.strip()

    chunks: list[TextChunk] = []

    step = chunk_size - overlap
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        chunk = text[start:end]

        chunks.append(
            TextChunk(
                index=chunk_index,
                text=chunk,
                character_count=len(chunk),
            )
        )

        chunk_index += 1

        if end >= len(text):
            break

        start += step

    return chunks
