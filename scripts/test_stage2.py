
from app.pdf_loader import extract_pdf
from app.chunking import create_document_chunks

PDF_PATH = "data/uploads/sample.pdf"

print("Starting Universal PDF Processing...\n")

# Step 1: Extract PDF
pages = extract_pdf(PDF_PATH)

print("Total pages:", len(pages))

# Step 2: Display extraction methods
for page in pages:

    print(
        f"Page {page['metadata']['page']}: "
        f"{page['metadata']['extraction_method']} | "
        f"Characters: {len(page['text'])}"
    )

# Step 3: Create chunks
chunks = create_document_chunks(
    pages,
    chunk_size=1000,
    chunk_overlap=150
)

print("\nTotal chunks:", len(chunks))

# Step 4: Display first chunk
if chunks:

    print("\nFirst chunk:")
    print(chunks[0]["text"][:500])

    print("\nMetadata:")
    print(chunks[0]["metadata"])

print("\nStage 2 processing completed!")

print("\nAll generated chunks:")

for chunk in chunks:

    print("\n--------------------")

    print("Chunk ID:", chunk["id"])
    print("Page:", chunk["metadata"]["page"])
    print("Length:", len(chunk["text"]))

    print("Text:")
    print(chunk["text"][:200])