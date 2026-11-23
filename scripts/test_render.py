
import pymupdf
from pathlib import Path

PDF_PATH = "data/uploads/sample.pdf"
OUTPUT_DIR = Path("data/rendered")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Starting PDF rendering...")

try:
    pdf = pymupdf.open(PDF_PATH)

    print("Total pages:", len(pdf))

    for index, page in enumerate(pdf):

        try:
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            output_path = OUTPUT_DIR / f"page_{index + 1}.png"

            pix.save(str(output_path))

            print(f"Page {index + 1}: Rendered successfully")

        except Exception as error:
            print(f"Page {index + 1}: Rendering failed")
            print("Reason:", error)

    pdf.close()

except Exception as error:
    print("Cannot open PDF:", error)

print("\nRendering test completed!")
