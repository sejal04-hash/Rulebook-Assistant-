
from pathlib import Path
import pymupdf

PDF_PATH = Path("data/uploads/sample.pdf")

print("Starting PDF inspection...")

if not PDF_PATH.exists():
    raise FileNotFoundError(PDF_PATH)

print("File size:", PDF_PATH.stat().st_size, "bytes")

try:
    pdf = pymupdf.open(PDF_PATH)

    print("Total pages:", len(pdf))
    print("Encrypted:", pdf.is_encrypted)

    for index, page in enumerate(pdf):

        try:
            text = page.get_text("text")
            images = page.get_images(full=True)

            print(f"\nPage {index + 1}")
            print("Text characters:", len(text.strip()))
            print("Images:", len(images))
            print("Preview:", repr(text[:150]))

        except Exception as error:
            print(f"Page {index + 1} error:", error)

    pdf.close()

except Exception as error:
    print("PDF inspection failed:", error)
