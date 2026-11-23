
from app.retrieval import hybrid_search
from app.llm import generate_answer


print("\n========== PDF RAG ASSISTANT ==========")

question = input("\nAsk a question about your PDF: ").strip()

if not question:
    print("Please enter a valid question.")

else:
    print("\nSearching relevant PDF chunks...")

    retrieved_chunks = hybrid_search(
        query=question,
        top_k=3,
        candidate_k=10
    )

    print(f"Retrieved {len(retrieved_chunks)} chunks.")

    print("\nGenerating answer using Ollama...")

    answer = generate_answer(
        question,
        retrieved_chunks
    )

    print("\n========== FINAL ANSWER ==========")

    print(answer)

    print("\n========== SOURCE PAGES ==========")

    pages = sorted({
        chunk["metadata"]["page"]
        for chunk in retrieved_chunks
    })

    print("Retrieved pages:", pages)
