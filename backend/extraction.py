"""Local text extraction.

Replaces Amazon Textract. Two paths, chosen by file extension:

- PDFs: text is pulled directly from the PDF via `pypdf`. This works
  for any text-based PDF regardless of page count — nothing here is
  special-cased for a particular number of pages.
- Images (png/jpg/etc.): OCR'd with `pytesseract`, which shells out to
  the local Tesseract binary. Install it separately (see README) —
  the Python package alone isn't enough.

If a PDF has no extractable text (e.g. it's a scanned image saved as
a PDF) and OCR isn't available, extraction returns an empty string and
the explain step reports that no readable text was found, rather than
raising.
"""

import os

from pypdf import PdfReader

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

# Keep the payload reasonable for the LLM call.
MAX_CHARS = 15000


def extract_text(file_path: str, file_name: str) -> str:
    ext = os.path.splitext(file_name)[1].lower()

    if ext == ".pdf":
        text = _extract_pdf(file_path)
    elif ext in IMAGE_EXTENSIONS:
        text = _extract_image(file_path)
    elif ext == ".txt":
        text = _extract_txt(file_path)
    else:
        # Unknown extension — try PDF parsing first, then OCR, rather
        # than refusing outright.
        text = _extract_pdf(file_path) or _extract_image(file_path)

    return text.strip()[:MAX_CHARS]


def _extract_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception:
        return ""


def _extract_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image

        with Image.open(file_path) as image:
            return pytesseract.image_to_string(image).strip()
    except Exception:
        # Missing Tesseract binary, unreadable image, etc. — degrade
        # to "no text found" rather than crashing the pipeline.
        return ""


def _extract_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""
