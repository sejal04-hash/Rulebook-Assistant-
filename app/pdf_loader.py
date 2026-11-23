
import pymupdf
import pytesseract
import hashlib
import io

from PIL import Image
from pathlib import Path


# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_pdf_from_bytes(
    pdf_bytes: bytes,
    filename: str
) -> list[dict]:

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    if not pdf_bytes:
        raise ValueError("PDF file is empty.")

    document_id = hashlib.sha256(
        pdf_bytes
    ).hexdigest()[:16]

    pages = []

    try:
        pdf = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        if pdf.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        total_pages = len(pdf)

        for page_index, page in enumerate(pdf):

            text = ""
            extraction_method = "text"

            # First try normal text extraction
            try:
                text = page.get_text("text").strip()
            except Exception as error:
                print(
                    f"Text extraction failed on page "
                    f"{page_index + 1}: {error}"
                )

            # If text is missing, use OCR
            if len(text) < 30:

                extraction_method = "ocr"

                try:
                    pix = page.get_pixmap(
                        matrix=pymupdf.Matrix(2, 2),
                        alpha=False
                    )

                    image = Image.open(
                        io.BytesIO(pix.tobytes("png"))
                    )

                    text = pytesseract.image_to_string(
                        image,
                        lang="eng",
                        config="--oem 3 --psm 3"
                    ).strip()

                except Exception as error:
                    print(
                        f"OCR failed on page "
                        f"{page_index + 1}: {error}"
                    )

                    text = ""

            if not text:
                print(
                    f"Warning: No text found on page "
                    f"{page_index + 1}"
                )

            pages.append({
                "text": text,
                "metadata": {
                    "document_id": document_id,
                    "source": Path(filename).name,
                    "page": page_index + 1,
                    "total_pages": total_pages,
                    "extraction_method": extraction_method
                }
            })

        pdf.close()

    except ValueError:
        raise
    except Exception as error:
        raise ValueError(
            f"PDF processing failed: {error}"
        )

    if not any(page["text"] for page in pages):
        raise ValueError(
            "No text could be extracted from this PDF."
        )

    return pages


def extract_pdf(pdf_path: str) -> list[dict]:

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    return extract_pdf_from_bytes(
        path.read_bytes(),
        path.name
    )
