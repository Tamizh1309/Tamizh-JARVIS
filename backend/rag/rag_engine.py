"""RAG Engine providing document knowledge retrieval and citation synthesis."""
import logging
from typing import Dict, Any, List, Optional
from rag.parser import DocumentParser
from rag.chunker import TextChunker
from rag.vector_store import DocumentVectorStore
from ai.provider import AIProvider, get_ai_provider

logger = logging.getLogger("tamizh_jarvis.rag.engine")


class RAGEngine:
    """Manages document ingestion, similarity retrieval, and cited answers."""

    def __init__(self, db_path: str = "jarvis.db", ai_provider: Optional[AIProvider] = None):
        self.store = DocumentVectorStore(db_path=db_path)
        self.ai = ai_provider or get_ai_provider()

    async def ingest_document(self, filename: str, content_bytes: bytes, file_type: str = "txt") -> Dict[str, Any]:
        raw_text = DocumentParser.extract_text(filename, content_bytes)
        if not raw_text.strip():
            raise ValueError(f"Could not extract meaningful text from file '{filename}'.")

        chunks = TextChunker.chunk_text(raw_text, chunk_size=400, overlap=50)
        if not chunks:
            raise ValueError(f"File '{filename}' yielded 0 text chunks.")

        doc_id = await self.store.insert_document(
            filename=filename,
            file_type=file_type,
            file_size=len(content_bytes),
            chunks=chunks
        )

        return {
            "document_id": doc_id,
            "filename": filename,
            "chunk_count": len(chunks),
            "file_size": len(content_bytes)
        }

    async def query(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        chunks = await self.store.search_chunks(query_text, top_k=top_k)

        if not chunks:
            # Fallback to general AI knowledge without false citations
            return {
                "answer": f"No relevant information was found in your uploaded documents regarding '{query_text}'.",
                "sources": [],
                "source_attribution": "General Knowledge (No matching document chunks)",
                "found_in_documents": False
            }

        # Build grounded context from top chunks
        context_str = "\n\n".join([
            f"[Source: {c['filename']} | Chunk {c['chunk_index']}]:\n{c['content']}"
            for c in chunks
        ])

        system_prompt = (
            "You are Tamizh JARVIS Document RAG assistant. "
            "Answer the user query strictly using the provided context chunks. "
            "Cite the source filename and chunk index in your explanation."
        )

        user_prompt = f"Context:\n{context_str}\n\nUser Question: {query_text}"

        try:
            answer = await self.ai.generate(prompt=user_prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.warning("RAG AI generation fallback: %s", str(e))
            primary = chunks[0]
            answer = f"According to your document '{primary['filename']}':\n{primary['content']}"

        primary_doc = chunks[0]["filename"]
        return {
            "answer": answer,
            "sources": chunks,
            "source_attribution": f"Document Knowledge ({primary_doc})",
            "found_in_documents": True
        }

    async def list_documents(self) -> List[Dict[str, Any]]:
        return await self.store.list_documents()

    async def delete_document(self, document_id: int) -> bool:
        return await self.store.delete_document(document_id)


_rag_engine_instance = None


def get_rag_engine(db_path: Optional[str] = None) -> RAGEngine:
    global _rag_engine_instance
    if db_path:
        return RAGEngine(db_path=db_path)
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance
