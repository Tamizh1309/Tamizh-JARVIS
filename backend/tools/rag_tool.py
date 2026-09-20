"""RAG Tool for querying uploaded user study and reference documents."""
from typing import Dict, Any, Optional
from tools.base_tool import BaseTool
from rag.rag_engine import get_rag_engine, RAGEngine


class RAGTool(BaseTool):
    """Tool for querying uploaded study notes, GATE materials, and resumes."""

    def __init__(self, rag_engine: Optional[RAGEngine] = None):
        self.engine = rag_engine or get_rag_engine()

    @property
    def name(self) -> str:
        return "rag_tool"

    @property
    def description(self) -> str:
        return "Retrieves information from uploaded personal study notes and documents with explicit citations."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        query_text = params.get("query") or params.get("question") or ""
        if not query_text.strip():
            return self.format_output(
                success=False,
                action="rag_query",
                data={},
                message="No search query provided to search documents."
            )

        result = await self.engine.query(query_text=query_text, top_k=3)
        return self.format_output(
            success=True,
            action="rag_query",
            data=result,
            message=result["answer"]
        )
