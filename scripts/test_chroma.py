
import chromadb
from pathlib import Path

db_path = Path("chroma_test_db").resolve()

print("Testing ChromaDB...")
print("Database path:", db_path)

client = chromadb.PersistentClient(
    path=str(db_path)
)

collection = client.get_or_create_collection(
    name="test_collection"
)

print("ChromaDB initialized successfully!")
print("Collection count:", collection.count())
