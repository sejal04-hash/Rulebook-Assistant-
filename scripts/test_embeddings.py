
from app.pdf_loader import extract_pdf
from app.chunking import create_document_chunks
from app.embeddings import generate_embeddings, generate_query_embedding


PDF_PATH = "data/uploads/sample.pdf"


print("Step 1: Extracting PDF...")

pages = extract_pdf(PDF_PATH)

print("Pages extracted:", len(pages))


print("\nStep 2: Creating chunks...")

chunks = create_document_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=150
)

print("Total chunks:", len(chunks))


print("\nStep 3: Generating embeddings...")

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = generate_embeddings(texts)

print("\nEmbedding generation completed!")

print("Embedding shape:", embeddings.shape)

print("Total vectors:", len(embeddings))

print("Dimensions per vector:", len(embeddings[0]))


print("\nFirst vector (first 10 values):")
print(embeddings[0][:10])


print("\nStep 4: Testing query embedding...")

query = "What is the course starting date?"

query_embedding = generate_query_embedding(query)

print("Query:", query)

print("Query embedding shape:", query_embedding.shape)

print("\nStage 3 embedding test completed!")
