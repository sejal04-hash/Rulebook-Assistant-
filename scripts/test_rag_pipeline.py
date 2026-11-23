
from pathlib import Path

from app.pdf_loader import extract_pdf
from app.chunking import create_document_chunks
from app.embeddings import (
    generate_embeddings,
    generate_query_embedding
)
from app.vector_store import (
    add_chunks,
    search_chunks,
    get_collection_count
)


# ==========================================
# STEP 1: PDF FILE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "data" / "uploads" / "sample.pdf"

print("\n========== PDF PROCESSING ==========")

print("PDF Path:", PDF_PATH)


# ==========================================
# STEP 2: EXTRACT TEXT FROM PDF
# ==========================================

pages = extract_pdf(str(PDF_PATH))

print("\nPDF extraction completed!")

print("Total pages:", len(pages))

for page in pages:
    print(
        f"Page {page['metadata']['page']}: "
        f"{len(page['text'])} characters"
    )


# ==========================================
# STEP 3: CREATE TEXT CHUNKS
# ==========================================

chunks = create_document_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=150
)

print("\nChunking completed!")

print("Total chunks:", len(chunks))


# ==========================================
# STEP 4: GENERATE BGE EMBEDDINGS
# ==========================================

print("\nGenerating BGE embeddings...")

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = generate_embeddings(texts)

print("\nEmbeddings generated successfully!")

print("Embedding shape:", embeddings.shape)


# ==========================================
# STEP 5: STORE IN CHROMADB
# ==========================================

print("\nStoring data in ChromaDB...")

add_chunks(
    chunks,
    embeddings
)

print(
    "Total stored chunks:",
    get_collection_count()
)


# ==========================================
# STEP 6: SEARCH USING A QUESTION
# ==========================================

print("\n========== SEARCH TEST ==========")

query = input("\nEnter your question about the PDF: ")

query_embedding = generate_query_embedding(query)

results = search_chunks(
    query_embedding,
    top_k=3
)


# ==========================================
# STEP 7: DISPLAY SEARCH RESULTS
# ==========================================

print("\n========== SEARCH RESULTS ==========")

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

if not documents:
    print("No relevant chunks found.")

else:
    for i, document in enumerate(documents):

        print(f"\nResult {i + 1}")

        print("Page:", metadatas[i]["page"])

        print("Distance:", distances[i])

        print("Text:")

        print(document)

        print("-" * 60)


print("\nRAG pipeline test completed!")
