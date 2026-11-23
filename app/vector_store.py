
import chromadb
from pathlib import Path


# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "pdf_chunks_v1"


# ==========================================
# 2. INITIALIZE CHROMADB
# ==========================================

CHROMA_PATH.mkdir(parents=True, exist_ok=True)

print("Connecting to ChromaDB...")
print("Database location:", CHROMA_PATH)

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

print("ChromaDB connected successfully!")


# ==========================================
# 3. STORE PDF CHUNKS AND EMBEDDINGS
# ==========================================

def add_chunks(chunks, embeddings):

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Chunks and embeddings count must match."
        )

    if not chunks:
        print("No chunks available to store.")
        return

    ids = [chunk["id"] for chunk in chunks]

    documents = [chunk["text"] for chunk in chunks]

    metadatas = [chunk["metadata"] for chunk in chunks]

    vectors = embeddings.tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=vectors
    )

    print(f"Successfully stored {len(chunks)} chunks!")


# ==========================================
# 4. SEARCH RELEVANT PDF CHUNKS
# ==========================================

def search_chunks(
    query_embedding,
    top_k=3,
    document_id=None
):

    filters = None

    if document_id:
        filters = {"document_id": document_id}

    # Count chunks matching the selected PDF
    matching_data = collection.get(
        where=filters,
        include=["metadatas"]
    )

    matching_count = len(matching_data["ids"])

    if matching_count == 0:
        print("No chunks found for this document.")

        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=min(top_k, matching_count),
        where=filters
    )

    return results


# ==========================================
# 5. GET TOTAL STORED CHUNKS
# ==========================================

def get_collection_count():

    return collection.count()


# ==========================================
# 6. GET ALL STORED CHUNKS
# ==========================================

def get_all_chunks():

    results = collection.get(
        include=["documents", "metadatas"]
    )

    all_chunks = []

    for i in range(len(results["ids"])):

        all_chunks.append({
            "id": results["ids"][i],
            "text": results["documents"][i],
            "metadata": results["metadatas"][i]
        })

    return all_chunks


# ==========================================
# 7. GET ALL UPLOADED DOCUMENTS
# ==========================================

def get_all_documents():

    results = collection.get(
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"]:

        if not metadata:
            continue

        document_id = metadata.get("document_id")

        if not document_id:
            continue

        if document_id not in documents:

            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("source", "Unknown"),
                "total_pages": metadata.get("total_pages", 0),
                "total_chunks": 0
            }

        documents[document_id]["total_chunks"] += 1

    return list(documents.values())


# ==========================================
# 8. DELETE A DOCUMENT
# ==========================================

def delete_document(document_id):

    if not document_id or not document_id.strip():
        raise ValueError("Document ID cannot be empty.")

    # Find chunks belonging to this document
    existing_data = collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    # Check whether document exists
    chunk_ids = existing_data["ids"]

    if not chunk_ids:
        return 0

    # Delete all chunks of the selected document
    collection.delete(
        ids=chunk_ids
    )

    print(
        f"Deleted document {document_id}: "
        f"{len(chunk_ids)} chunks removed."
    )

    return len(chunk_ids)
