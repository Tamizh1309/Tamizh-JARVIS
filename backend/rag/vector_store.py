"""Lightweight Vector / TF-IDF Similarity Store for RAG."""
import math
import re
import json
from collections import Counter
from typing import List, Dict, Any, Optional
import aiosqlite


class DocumentVectorStore:
    """Manages document chunks and cosine similarity search over token vectors."""

    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    token_vector TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                );
            """)
            await db.commit()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        stopwords = {"the", "and", "for", "with", "this", "that", "from", "are", "was", "has", "have", "you"}
        return [w for w in words if w not in stopwords]

    @classmethod
    def compute_tf_vector(cls, text: str) -> Dict[str, float]:
        tokens = cls.tokenize(text)
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = float(len(tokens))
        return {term: count / total for term, count in counts.items()}

    @staticmethod
    def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        if not intersection:
            return 0.0
        dot_product = sum(vec_a[t] * vec_b[t] for t in intersection)
        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)

    async def insert_document(self, filename: str, file_type: str, file_size: int, chunks: List[Dict[str, Any]]) -> int:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO documents (filename, file_type, file_size, chunk_count) VALUES (?, ?, ?, ?)",
                (filename, file_type, file_size, len(chunks))
            )
            doc_id = cursor.lastrowid

            for c in chunks:
                vec = self.compute_tf_vector(c["content"])
                await db.execute(
                    "INSERT INTO document_chunks (document_id, filename, chunk_index, content, token_vector) VALUES (?, ?, ?, ?, ?)",
                    (doc_id, filename, c["chunk_index"], c["content"], json.dumps(vec))
                )
            await db.commit()
            return doc_id

    async def search_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        await self.init_db()
        query_vec = self.compute_tf_vector(query)
        if not query_vec:
            return []

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT id, document_id, filename, chunk_index, content, token_vector FROM document_chunks")
            rows = await cursor.fetchall()

        scored = []
        for r in rows:
            chunk_vec = json.loads(r["token_vector"])
            score = self.cosine_similarity(query_vec, chunk_vec)
            if score > 0.05:  # Relevance threshold
                scored.append({
                    "chunk_id": r["id"],
                    "document_id": r["document_id"],
                    "filename": r["filename"],
                    "chunk_index": r["chunk_index"],
                    "content": r["content"],
                    "similarity_score": round(score, 4)
                })

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]

    async def list_documents(self) -> List[Dict[str, Any]]:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT id, filename, file_type, file_size, chunk_count, uploaded_at FROM documents ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def delete_document(self, document_id: int) -> bool:
        await self.init_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM document_chunks WHERE document_id = ?", (document_id,))
            cursor = await db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            await db.commit()
            return cursor.rowcount > 0
