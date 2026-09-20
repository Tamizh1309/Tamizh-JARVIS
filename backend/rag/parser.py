"""Document text extraction for TXT, Markdown, and PDF formats."""
import re
import logging

logger = logging.getLogger("tamizh_jarvis.rag.parser")


class DocumentParser:
    """Extracts clean plain-text strings from diverse file formats."""

    @staticmethod
    def parse_txt(content_bytes: bytes) -> str:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return content_bytes.decode("latin-1", errors="ignore")

    @staticmethod
    def parse_markdown(content_bytes: bytes) -> str:
        text = DocumentParser.parse_txt(content_bytes)
        # Clean markdown syntax while preserving textual meaning
        text = re.sub(r"#+\s*", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        text = re.sub(r"[*_`~]", "", text)
        return text

    @staticmethod
    def parse_pdf(content_bytes: bytes) -> str:
        """Lightweight text extraction from PDF stream."""
        try:
            # Fallback stream string extraction for text objects
            raw = content_bytes.decode("latin-1", errors="ignore")
            # Extract text blocks inside BT ... ET operators
            text_blocks = re.findall(r"BT[\s\S]*?ET", raw)
            if text_blocks:
                extracted = []
                for b in text_blocks:
                    strings = re.findall(r"\(([^\)]+)\)", b)
                    extracted.extend(strings)
                if extracted:
                    return " ".join(extracted)
            
            # General stream fallback
            clean = re.sub(r"[^\x20-\x7E\n\t]", " ", raw)
            words = [w for w in clean.split() if len(w) > 2 and w.isalnum()]
            return " ".join(words[:2000])
        except Exception as e:
            logger.warning("PDF stream parse error: %s", str(e))
            return content_bytes.decode("utf-8", errors="ignore")

    @classmethod
    def extract_text(cls, filename: str, content_bytes: bytes) -> str:
        fn_lower = filename.lower()
        if fn_lower.endswith(".pdf"):
            return cls.parse_pdf(content_bytes)
        elif fn_lower.endswith((".md", ".markdown")):
            return cls.parse_markdown(content_bytes)
        else:
            return cls.parse_txt(content_bytes)
