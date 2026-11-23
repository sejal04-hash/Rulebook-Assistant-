
import re

from rank_bm25 import BM25Okapi

from app.vector_store import get_all_chunks, search_chunks
from app.embeddings import generate_query_embedding


# ==========================================
# 1. TOKENIZE TEXT
# ==========================================

def tokenize(text):

    return re.findall(
        r"\b\w+\b",
        text.lower()
    )


# ==========================================
# 2. RECIPROCAL RANK FUSION
# ==========================================

def reciprocal_rank_fusion(
    bm25_results,
    vector_results,
    k=60
):

    scores = {}

    # Add BM25 ranking scores
    for rank, chunk in enumerate(bm25_results, start=1):

        chunk_id = chunk["id"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0)
            + 1 / (k + rank)
        )

    # Add vector search ranking scores
    for rank, chunk in enumerate(vector_results, start=1):

        chunk_id = chunk["id"]

        scores[chunk_id] = (
            scores.get(chunk_id, 0)
            + 1 / (k + rank)
        )

    # Sort by highest combined score
    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    return ranked_ids, scores


# ==========================================
# 3. HYBRID SEARCH
# ==========================================

def hybrid_search(
    query,
    top_k=3,
    candidate_k=10,
    document_id=None
):

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not document_id or not document_id.strip():
        raise ValueError("Please provide a valid document_id.")

    # ======================================
    # GET ALL STORED CHUNKS
    # ======================================

    all_chunks = get_all_chunks()

    # Keep only selected PDF chunks
    chunks = [
        chunk
        for chunk in all_chunks
        if chunk["metadata"].get("document_id") == document_id
    ]

    if not chunks:
        print("No chunks found for this document.")
        return []

    # Create ID-to-chunk mapping
    chunk_map = {
        chunk["id"]: chunk
        for chunk in chunks
    }

    # ======================================
    # BM25 KEYWORD SEARCH
    # ======================================

    tokenized_corpus = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = tokenize(query)

    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )

    # Keep only chunks with actual keyword matches
    bm25_results = [
        chunks[i]
        for i in bm25_indices[:candidate_k]
        if bm25_scores[i] > 0
    ]

    # ======================================
    # VECTOR SEMANTIC SEARCH
    # ======================================

    query_embedding = generate_query_embedding(query)

    vector_data = search_chunks(
        query_embedding,
        top_k=min(candidate_k, len(chunks)),
        document_id=document_id
    )

    vector_ids = vector_data["ids"][0]

    vector_results = [
        chunk_map[chunk_id]
        for chunk_id in vector_ids
        if chunk_id in chunk_map
    ]

    # ======================================
    # COMBINE USING RRF
    # ======================================

    ranked_ids, combined_scores = reciprocal_rank_fusion(
        bm25_results,
        vector_results
    )

    # ======================================
    # RETURN FINAL RESULTS
    # ======================================

    final_results = []

    for chunk_id in ranked_ids[:top_k]:

        chunk = chunk_map[chunk_id].copy()

        chunk["rrf_score"] = combined_scores[chunk_id]

        final_results.append(chunk)

    return final_results
