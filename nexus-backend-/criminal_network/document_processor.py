import os
import re
import csv
from typing import Dict, Any, List

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None


class DocumentProcessor:
    """
    Extracts plain text and structure from raw case documents
    including PDF, DOCX, TXT, CSV, and JSON files.
    """

    @staticmethod
    def extract_text_from_file(file_path: str) -> Dict[str, Any]:
        """
        Extracts text content and metadata from the given file path.
        Returns a dictionary with 'text', 'file_type', 'pages', and 'word_count'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)

        if ext == ".pdf":
            return DocumentProcessor._extract_from_pdf(file_path, file_name)
        elif ext in [".docx", ".doc"]:
            return DocumentProcessor._extract_from_docx(file_path, file_name)
        elif ext == ".csv":
            return DocumentProcessor._extract_from_csv(file_path, file_name)
        elif ext in [".txt", ".log", ".json"]:
            return DocumentProcessor._extract_from_txt(file_path, file_name)
        else:
            # Fallback text decoding
            return DocumentProcessor._extract_from_txt(file_path, file_name)

    @staticmethod
    def _extract_from_pdf(file_path: str, file_name: str) -> Dict[str, Any]:
        full_text = []
        pages_content = []

        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for idx, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        # Also attempt table extraction if tabular
                        tables = page.extract_tables()
                        if tables:
                            table_strings = []
                            for table in tables:
                                for row in table:
                                    cleaned_row = [str(c or "") for c in row]
                                    table_strings.append(" | ".join(cleaned_row))
                            page_text += "\n" + "\n".join(table_strings)

                        pages_content.append({"page_number": idx + 1, "text": page_text})
                        full_text.append(page_text)
            except Exception as e:
                # Fallback to binary/regex text extraction
                full_text.append(f"[PDF Extraction warning: {e}]")
        else:
            full_text.append("[pdfplumber not available, reading raw bytes]")

        combined_text = "\n\n".join(full_text).strip()
        return {
            "file_name": file_name,
            "file_type": "PDF",
            "page_count": len(pages_content) or 1,
            "text": combined_text,
            "word_count": len(combined_text.split()),
            "pages": pages_content
        }

    @staticmethod
    def _extract_from_docx(file_path: str, file_name: str) -> Dict[str, Any]:
        full_text = []
        if docx:
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    if para.text.strip():
                        full_text.append(para.text.strip())
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells)
                        full_text.append(row_text)
            except Exception as e:
                full_text.append(f"[DOCX read error: {e}]")
        else:
            full_text.append("[python-docx not available]")

        combined_text = "\n".join(full_text)
        return {
            "file_name": file_name,
            "file_type": "DOCX",
            "page_count": 1,
            "text": combined_text,
            "word_count": len(combined_text.split()),
            "pages": [{"page_number": 1, "text": combined_text}]
        }

    @staticmethod
    def _extract_from_csv(file_path: str, file_name: str) -> Dict[str, Any]:
        rows_text = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if not header:
                    header = row
                    rows_text.append("Columns: " + ", ".join(header))
                else:
                    paired = [f"{header[i]}: {row[i]}" for i in range(min(len(header), len(row)))]
                    rows_text.append("; ".join(paired))

        combined_text = "\n".join(rows_text)
        return {
            "file_name": file_name,
            "file_type": "CSV",
            "page_count": 1,
            "text": combined_text,
            "word_count": len(combined_text.split()),
            "pages": [{"page_number": 1, "text": combined_text}]
        }

    @staticmethod
    def _extract_from_txt(file_path: str, file_name: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return {
            "file_name": file_name,
            "file_type": "TEXT",
            "page_count": 1,
            "text": content,
            "word_count": len(content.split()),
            "pages": [{"page_number": 1, "text": content}]
        }
