
from pypdf import PdfReader

PDF_PATH = "data/uploads/sample.pdf"

print("Starting PyPDF inspection...")

try:
    reader = PdfReader(PDF_PATH)

    print("Total pages:", len(reader.pages))

    for index, page in enumerate(reader.pages[:5]):

        text = page.extract_text() or ""

        print(f"\nPage {index + 1}")
        print("Characters:", len(text))
        print("Preview:")
        print(text[:300])

    print("\nPyPDF test completed!")

except Exception as error:
    print("PyPDF extraction failed:", error)
