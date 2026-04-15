from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List


@dataclass
class Document:
    page_content: str
    metadata: dict = field(default_factory=dict)


def split_documents(
    documents: Iterable[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:
    chunks: List[Document] = []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    step = chunk_size - chunk_overlap

    for document in documents:
        text = document.page_content or ""
        metadata = dict(document.metadata)

        if not text:
            chunks.append(Document(page_content="", metadata=metadata))
            continue

        for start in range(0, len(text), step):
            end = start + chunk_size
            chunk_text = text[start:end]
            if chunk_text:
                chunks.append(Document(page_content=chunk_text, metadata=dict(metadata)))

    return chunks


def enrich_chunks(chunks: Iterable[Document]) -> List[Document]:
    enriched_chunks: List[Document] = []

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        metadata = dict(chunk.metadata)

        metadata["filename"] = source.split("/")[-1]
        metadata["page_number"] = metadata.get("page", -1)
        metadata["upload_date"] = datetime.now().strftime("%Y-%m-%d")
        metadata["source_type"] = "paper" if "paper" in source else "notes"

        enriched_chunks.append(Document(page_content=chunk.page_content, metadata=metadata))

    return enriched_chunks


def filter_chunks(chunks: Iterable[Document], **filters):
    filtered = []

    for chunk in chunks:
        match = True

        for key, value in filters.items():
            if chunk.metadata.get(key) != value:
                match = False
                break

        if match:
            filtered.append(chunk)

    return filtered


documents = [
    Document(
        page_content=(
            "This is a sample document used to demonstrate chunking and metadata enrichment. "
            "It is long enough to create more than one chunk when the chunk size is small."
        ),
        metadata={"source": "paper1.pdf", "page": 0},
    ),
    Document(
        page_content="These are notes from a meeting.",
        metadata={"source": "meeting-notes.txt", "page": 1},
    ),
]

chunks = enrich_chunks(split_documents(documents))


if __name__ == "__main__":
    print(f"Total chunks: {len(chunks)}")

    result1 = filter_chunks(chunks, filename="paper1.pdf")
    print(f"Chunks from paper1.pdf: {len(result1)}")

    result2 = filter_chunks(chunks, page_number=0)
    print(f"Chunks from page 0: {len(result2)}")

    result3 = filter_chunks(chunks, source_type="notes")
    print(f"Chunks from notes: {len(result3)}")

    if result1:
        print("\nSample chunk content:\n")
        print(result1[0].page_content[:500])
