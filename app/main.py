
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.pdf_loader import extract_pdf_from_bytes
from app.chunking import create_document_chunks
from app.embeddings import generate_embeddings

from pathlib import Path

from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.vector_store import (
    add_chunks,
    get_all_documents,
    delete_document
)

from app.retrieval import hybrid_search
from app.llm import generate_answer


# ==========================================
# 1. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Universal PDF RAG Assistant",
    description="Upload PDFs and ask questions using AI.",
    version="1.0.0"
)

# ==========================================
# FRONTEND CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

# HTML templates folder
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

# CSS and JavaScript folder
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)
# ==========================================
# 2. QUESTION REQUEST MODEL
# ==========================================

class QuestionRequest(BaseModel):

    question: str
    document_id: str


# ==========================================
# 3. HOME API
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Welcome to Universal PDF RAG Assistant!",
        "status": "running"
    }


# ==========================================
# 4. HEALTH CHECK API
# ==========================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "message": "RAG Assistant API is working!"
    }


# ==========================================
# 5. PDF UPLOAD API
# ==========================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:

        pdf_bytes = await file.read()

        if not pdf_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        pages = extract_pdf_from_bytes(
            pdf_bytes,
            file.filename
        )

        chunks = create_document_chunks(
            pages,
            chunk_size=1000,
            chunk_overlap=150
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail="No text chunks found in PDF."
            )

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        add_chunks(
            chunks,
            embeddings
        )

        document_id = pages[0]["metadata"]["document_id"]

        return {
            "message": "PDF uploaded and processed successfully!",
            "filename": file.filename,
            "document_id": document_id,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "status": "success"
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )

    finally:
        await file.close()


# ==========================================
# 6. ASK QUESTION API
# ==========================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()
    document_id = request.document_id.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not document_id:

        raise HTTPException(
            status_code=400,
            detail="Document ID is required."
        )

    try:

        retrieved_chunks = hybrid_search(
            query=question,
            top_k=3,
            candidate_k=10,
            document_id=document_id
        )

        if not retrieved_chunks:

            raise HTTPException(
                status_code=404,
                detail="No relevant information found in the selected PDF."
            )

        answer = generate_answer(
            question,
            retrieved_chunks
        )

        source_pages = sorted({
            chunk["metadata"]["page"]
            for chunk in retrieved_chunks
        })

        return {
            "question": question,
            "document_id": document_id,
            "answer": answer,
            "source_pages": source_pages,
            "retrieved_chunks": len(retrieved_chunks),
            "status": "success"
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Question processing failed: {str(error)}"
        )


# ==========================================
# 7. LIST ALL UPLOADED DOCUMENTS
# ==========================================

@app.get("/documents")
def list_documents():

    try:

        documents = get_all_documents()

        return {
            "total_documents": len(documents),
            "documents": documents,
            "status": "success"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve documents: {str(error)}"
        )


# ==========================================
# 8. DELETE A DOCUMENT
# ==========================================

@app.delete("/documents/{document_id}")
def remove_document(document_id: str):

    try:

        deleted_chunks = delete_document(document_id)

        if deleted_chunks == 0:

            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        return {
            "message": "Document deleted successfully!",
            "document_id": document_id,
            "deleted_chunks": deleted_chunks,
            "status": "success"
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Document deletion failed: {str(error)}"
        )


# ==========================================
# FRONTEND HOME PAGE
# ==========================================

@app.get("/ui", include_in_schema=False)
async def frontend(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )