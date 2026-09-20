"""Document upload, management, and RAG knowledge query endpoints."""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from rag.rag_engine import get_rag_engine, RAGEngine

router = APIRouter()


class DocumentUploadRequest(BaseModel):
    filename: str
    content: str
    file_type: Optional[str] = "txt"


class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


@router.post("/upload")
async def upload_document_json(request: DocumentUploadRequest):
    """Ingests a document via JSON string content."""
    filename = request.filename.strip()
    content = request.content.strip()

    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    if not content:
        raise HTTPException(status_code=400, detail="Document content cannot be empty.")

    # Validation: File size & safety
    content_bytes = content.encode("utf-8")
    if len(content_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Document exceeds maximum allowable size (10MB).")

    allowed_exts = (".txt", ".md", ".markdown", ".pdf")
    if not any(filename.lower().endswith(ext) for ext in allowed_exts):
        raise HTTPException(status_code=400, detail=f"Unsupported file type for '{filename}'. Allowed: .txt, .md, .pdf")

    engine = get_rag_engine()
    try:
        res = await engine.ingest_document(
            filename=filename,
            content_bytes=content_bytes,
            file_type=request.file_type or "txt"
        )
        return {"success": True, "data": res, "message": f"Successfully ingested '{filename}' into knowledge base."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_uploaded_documents():
    """Lists all user documents indexed in RAG knowledge base."""
    engine = get_rag_engine()
    docs = await engine.list_documents()
    return {"success": True, "documents": docs, "total_documents": len(docs)}


@router.delete("/{document_id}")
async def delete_document(document_id: int):
    """Deletes a document and all its associated semantic chunks."""
    engine = get_rag_engine()
    deleted = await engine.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found.")
    return {"success": True, "message": f"Document #{document_id} deleted successfully."}


@router.post("/query")
async def query_knowledge_base(request: RAGQueryRequest):
    """Performs semantic similarity retrieval and citation answering over documents."""
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")

    engine = get_rag_engine()
    result = await engine.query(query_text=query_text, top_k=request.top_k or 3)
    return {"success": True, "data": result}
