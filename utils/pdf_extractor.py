import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    VentureScope PDF Extractor

    Features:
    - Native text extraction
    - OCR fallback
    - Table extraction
    - Metadata extraction
    - Structured output for agents
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

        logger.info(
            f"Initialized PDF extractor for: {pdf_path.split('/')[-1]}"
        )

    # ---------------------------------------------------
    # TEXT EXTRACTION
    # ---------------------------------------------------
    def extract_text(self) -> str:
        text = ""

        for page in self.doc:
            text += page.get_text()

        # OCR fallback
        if len(text.strip()) < 1000:
            logger.warning(
                "Low text extraction detected. Running OCR fallback..."
            )
            text = self._run_ocr()

        logger.info(f"Extracted {len(text)} characters")
        return text

    def _run_ocr(self) -> str:
        ocr_text = ""

        for page in self.doc:
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            ocr_text += pytesseract.image_to_string(img)

        return ocr_text

    # ---------------------------------------------------
    # TABLE EXTRACTION
    # ---------------------------------------------------
    def extract_tables(self):
        tables = []

        try:
            for page_num, page in enumerate(self.doc):
                blocks = page.get_text("blocks")

                for block in blocks:
                    block_text = block[4]

                    if "|" in block_text or "\t" in block_text:
                        tables.append({
                            "page": page_num,
                            "content": block_text
                        })

        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")

        logger.info(f"Extracted {len(tables)} table(s)")
        return tables

    # ---------------------------------------------------
    # METADATA
    # ---------------------------------------------------
    def extract_metadata(self):
        try:
            metadata = self.doc.metadata or {}

            return {
                "title": metadata.get("title"),
                "author": metadata.get("author"),
                "producer": metadata.get("producer"),
                "page_count": len(self.doc),
                "file_name": self.pdf_path.split("/")[-1],
            }

        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {}

    # ---------------------------------------------------
    # STRUCTURED DATA (NEW — REQUIRED)
    # ---------------------------------------------------
    def extract_structured_data(self):
        """
        Main method used by DocumentIngestionAgent.
        """

        logger.info("Running structured data extraction...")

        text = self.extract_text()
        tables = self.extract_tables()
        metadata = self.extract_metadata()

        structured_data = {
            "raw_text": text,
            "tables": tables,
            "metadata": metadata,
            "source_file": self.pdf_path,
        }

        return structured_data

    # ---------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------
    def close(self):
        if self.doc:
            self.doc.close()
            logger.info("PDF document closed")
