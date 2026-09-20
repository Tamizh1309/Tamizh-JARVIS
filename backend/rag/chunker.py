"""Text chunking utility with sliding window."""
from typing import List, Dict, Any


class TextChunker:
    """Splits continuous textual documents into semantic, indexed chunks."""

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[Dict[str, Any]]:
        cleaned = text.strip()
        if not cleaned:
            return []

        chunks = []
        start = 0
        text_len = len(cleaned)
        chunk_idx = 0

        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # Avoid cutting words in half when possible
            if end < text_len:
                space_pos = cleaned.rfind(" ", start, end)
                if space_pos > start + 100:
                    end = space_pos

            chunk_content = cleaned[start:end].strip()
            if chunk_content:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": chunk_content,
                    "char_length": len(chunk_content)
                })
                chunk_idx += 1

            start = end - overlap if end < text_len else text_len
            if start >= end:
                start = end

        return chunks
