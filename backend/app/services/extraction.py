"""
Extracts plain text from a wide range of uploaded file types so they
can be chunked + embedded uniformly. Supports PDF, DOCX, CSV, XLSX,
TXT/MD, and images via OCR.
"""
import io
import csv
import logging
import PyPDF2
import docx
import openpyxl
from PIL import Image
logger = logging.getLogger(__name__)
SUPPORTED_EXTENSIONS = {
    "pdf", "docx", "doc", "csv", "xlsx", "xls",
    "txt", "md", "json", "jpg", "jpeg", "png", "tiff", "bmp",
}
def extract_text(file_path: str, original_filename: str) -> str:
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    try:
        if ext == "pdf":
            return _extract_pdf(file_bytes)
        elif ext in ("docx", "doc"):
            return _extract_docx(file_bytes)
        elif ext == "csv":
            return _extract_csv(file_bytes)
        elif ext in ("xlsx", "xls"):
            return _extract_xlsx(file_bytes)

        elif ext in ("txt", "md", "json"):
            return file_bytes.decode("utf-8", errors="ignore")
        elif ext in ("jpg", "jpeg", "png", "tiff", "bmp"):
            return _extract_image_ocr(file_bytes)
        else:
            logger.warning("Unsupported file extension: %s", ext)
            return ""
    except Exception as e:
        logger.exception("Extraction failed for %s", original_filename)
        raise
def _extract_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for i, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        if txt.strip():
            pages.append(f"[Page {i + 1}]\n{txt}")
    return "\n\n".join(pages)
def _extract_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts)
def _extract_csv(file_bytes: bytes) -> str:
    content = file_bytes.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return ""
    header = rows[0]
    lines = []
    for row in rows[1:]:
        pairs = [f"{h}: {v}" for h, v in zip(header, row) if v]
        if pairs:
            lines.append(", ".join(pairs))
    return "\n".join(lines)
def _extract_xlsx(file_bytes: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    text_parts = []
    for sheet in wb.worksheets:
        text_parts.append(f"[Sheet: {sheet.title}]")
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        header = rows[0]
        for row in rows[1:]:
            pairs = [f"{h}: {v}" for h, v in zip(header, row) if v is not None and h is not None]
            if pairs:

                text_parts.append(", ".join(pairs))
    return "\n".join(text_parts)
def _extract_image_ocr(file_bytes: bytes) -> str:
    try:
        import pytesseract
        img = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(img)
    except ImportError:
        logger.warning("pytesseract not installed; skipping OCR")
        return ""
    except Exception as e:
        if "tesseract" in str(e).lower():
            logger.warning("Tesseract binary not installed; skipping OCR")
            return ""
        raise
