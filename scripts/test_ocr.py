
from pathlib import Path
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

IMAGE_DIR = Path("data/rendered")

print("Starting OCR test...")

if not IMAGE_DIR.exists():
    raise FileNotFoundError("data/rendered folder not found")

image_files = sorted(IMAGE_DIR.glob("page_*.png"))

if not image_files:
    raise FileNotFoundError("No rendered page images found")

for image_path in image_files:

    print(f"\nProcessing: {image_path.name}")

    image = Image.open(image_path)

    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--oem 3 --psm 3"
    )

    print("Extracted characters:", len(text.strip()))
    print("Text preview:")
    print(text[:500])

    output_path = image_path.with_suffix(".txt")

    output_path.write_text(
        text,
        encoding="utf-8"
    )

print("\nOCR testing completed!")
