
from app.retrieval import hybrid_search


print("========== HYBRID SEARCH TEST ==========")

query = input("Enter your question: ")

results = hybrid_search(
    query,
    top_k=3,
    candidate_k=10
)

print("\n========== FINAL RESULTS ==========")

if not results:

    print("No relevant results found.")

else:

    for i, chunk in enumerate(results, start=1):

        print(f"\nResult {i}")

        print("Page:", chunk["metadata"]["page"])

        print("RRF Score:", chunk["rrf_score"])

        print("Text:")

        print(chunk["text"])

        print("-" * 60)

print("\nHybrid search completed!")
