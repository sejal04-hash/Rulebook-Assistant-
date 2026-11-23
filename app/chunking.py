
import re


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Invalid chunk_overlap")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind(
                "\n\n",
                start + chunk_size // 2,
                end
            )

            if boundary == -1:
                boundary = text.rfind(
                    " ",
                    start + chunk_size // 2,
                    end
                )

            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(start + 1, end - chunk_overlap)

    return chunks


def create_document_chunks(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> list[dict]:

    all_chunks = []
    chunk_index = 0

    for page_data in pages:

        page_text = page_data["text"]
        metadata = page_data["metadata"]

        page_chunks = split_into_chunks(
            page_text,
            chunk_size,
            chunk_overlap
        )

        for chunk in page_chunks:

            all_chunks.append({
                "id": f"{metadata['document_id']}_{chunk_index}",
                "text": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index
                }
            })

            chunk_index += 1

    return all_chunks
