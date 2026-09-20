"""
TAMIZH JARVIS — Phase 11 Complete Test Suite
Tests: RAG, Voice, Notifications, Study Insights, Coding Workspace, Memory Relevance
"""
import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from memory.memory_manager import MemoryManager
from rag.chunker import TextChunker
from rag.parser import DocumentParser
from rag.vector_store import DocumentVectorStore
from rag.rag_engine import RAGEngine
from notifications.scheduler import NotificationManager
from study.insights import StudyInsightsEngine
from tools.rag_tool import RAGTool
from tools.coding_tool import CodingTool
from security.risk_classifier import RiskClassifier, RiskLevel


# ================================================================
# 1. DOCUMENT PARSER
# ================================================================
def test_p11_parser_txt():
    text = "DBMS Normalization: 1NF removes repeating groups. 2NF eliminates partial dependencies."
    result = DocumentParser.extract_text("notes.txt", text.encode("utf-8"))
    assert "DBMS" in result and "Normalization" in result


def test_p11_parser_markdown():
    md = "# Gate Notes\n\n## DBMS\nNormalization splits **tables** to reduce redundancy."
    result = DocumentParser.extract_text("notes.md", md.encode("utf-8"))
    assert "DBMS" in result
    assert "#" not in result


def test_p11_parser_pdf_stream():
    fake_pdf = b"BT (DBMS Transactions ACID Properties) Tj ET"
    result = DocumentParser.extract_text("notes.pdf", fake_pdf)
    assert isinstance(result, str) and len(result) > 0


# ================================================================
# 2. TEXT CHUNKER
# ================================================================
def test_p11_chunker_basic():
    chunks = TextChunker.chunk_text("A" * 1200, chunk_size=400, overlap=50)
    assert len(chunks) >= 3
    for c in chunks:
        assert c["char_length"] > 0 and "chunk_index" in c


def test_p11_chunker_empty():
    assert TextChunker.chunk_text("") == []


def test_p11_chunker_short():
    chunks = TextChunker.chunk_text("Short content.", chunk_size=400, overlap=50)
    assert len(chunks) == 1 and chunks[0]["content"] == "Short content."


# ================================================================
# 3. VECTOR STORE
# ================================================================
@pytest.mark.asyncio
async def test_p11_vector_store_insert_and_search(tmp_path):
    store = DocumentVectorStore(db_path=str(tmp_path / "vs.db"))
    chunks = [
        {"chunk_index": 0, "content": "DBMS normalization reduces data redundancy by decomposing tables."},
        {"chunk_index": 1, "content": "Binary search runs in O(log N) time on sorted arrays."},
    ]
    doc_id = await store.insert_document("notes.txt", "txt", 1000, chunks)
    assert doc_id > 0
    results = await store.search_chunks("normalization database tables", top_k=2)
    assert len(results) >= 1 and results[0]["filename"] == "notes.txt"


@pytest.mark.asyncio
async def test_p11_vector_store_delete(tmp_path):
    store = DocumentVectorStore(db_path=str(tmp_path / "vs_del.db"))
    doc_id = await store.insert_document("g.txt", "txt", 100, [{"chunk_index": 0, "content": "GATE OS scheduling"}])
    assert await store.delete_document(doc_id) is True
    docs = await store.list_documents()
    assert not any(d["id"] == doc_id for d in docs)


# ================================================================
# 4. RAG ENGINE
# ================================================================
@pytest.mark.asyncio
async def test_p11_rag_ingest_and_query(tmp_path):
    engine = RAGEngine(db_path=str(tmp_path / "rag.db"))
    content = b"DBMS Normalization: 1NF atomic. 2NF partial deps. 3NF transitive deps. BCNF."
    res = await engine.ingest_document("dbms.txt", content, file_type="txt")
    assert res["document_id"] > 0 and res["chunk_count"] >= 1
    qr = await engine.query("What is normalization in DBMS?", top_k=2)
    assert "found_in_documents" in qr and isinstance(qr["sources"], list)


@pytest.mark.asyncio
async def test_p11_rag_no_docs(tmp_path):
    engine = RAGEngine(db_path=str(tmp_path / "empty.db"))
    qr = await engine.query("Explain Dijkstra algorithm", top_k=3)
    assert qr["found_in_documents"] is False
    assert "No relevant information" in qr["answer"]


@pytest.mark.asyncio
async def test_p11_rag_delete(tmp_path):
    engine = RAGEngine(db_path=str(tmp_path / "del.db"))
    res = await engine.ingest_document("os.txt", b"OS process scheduling Round Robin preemptive")
    assert await engine.delete_document(res["document_id"]) is True


# ================================================================
# 5. RAG TOOL
# ================================================================
@pytest.mark.asyncio
async def test_p11_rag_tool_empty_query(tmp_path):
    tool = RAGTool(rag_engine=RAGEngine(db_path=str(tmp_path / "rt.db")))
    result = await tool.execute({"query": ""})
    assert result["success"] is False


@pytest.mark.asyncio
async def test_p11_rag_tool_no_docs(tmp_path):
    tool = RAGTool(rag_engine=RAGEngine(db_path=str(tmp_path / "rt2.db")))
    result = await tool.execute({"query": "Explain SQL joins"})
    assert result["success"] is True and result["data"]["found_in_documents"] is False


# ================================================================
# 6. NOTIFICATIONS
# ================================================================
@pytest.mark.asyncio
async def test_p11_notification_schedule(tmp_path):
    mgr = NotificationManager(db_path=str(tmp_path / "notif.db"))
    n = await mgr.schedule_notification("Study Reminder", "Revise DBMS tonight.", "2026-09-20T20:00:00")
    assert n["id"] > 0 and n["status"] == "PENDING"


@pytest.mark.asyncio
async def test_p11_notification_list(tmp_path):
    mgr = NotificationManager(db_path=str(tmp_path / "notif2.db"))
    await mgr.schedule_notification("A", "Msg A")
    await mgr.schedule_notification("B", "Msg B")
    pending = await mgr.get_pending_notifications()
    assert len(pending) >= 2


@pytest.mark.asyncio
async def test_p11_notification_dismiss(tmp_path):
    mgr = NotificationManager(db_path=str(tmp_path / "notif3.db"))
    n = await mgr.schedule_notification("Alert", "Test dismissal.")
    assert await mgr.dismiss_notification(n["id"]) is True
    pending = await mgr.get_pending_notifications()
    assert not any(x["id"] == n["id"] for x in pending)


# ================================================================
# 7. STUDY INSIGHTS
# ================================================================
@pytest.mark.asyncio
async def test_p11_study_insights(tmp_path):
    mem = MemoryManager(db_path=str(tmp_path / "si.db"))
    await mem.initialize()
    await mem.long_term.log_study_session(subject="DBMS", topic="Normalization", duration_minutes=45)
    await mem.long_term.log_study_session(subject="OS", topic="Scheduling", duration_minutes=60)
    insights = await StudyInsightsEngine(mem).calculate_insights()
    assert "study_streak_days" in insights
    assert insights["total_study_minutes_week"] >= 105
    assert "retention_forecast" in insights
    await mem.long_term.close()


@pytest.mark.asyncio
async def test_p11_study_insights_empty(tmp_path):
    mem = MemoryManager(db_path=str(tmp_path / "si_empty.db"))
    await mem.initialize()
    insights = await StudyInsightsEngine(mem).calculate_insights()
    assert insights["study_streak_days"] == 0
    assert insights["total_study_minutes_week"] == 0
    await mem.long_term.close()


# ================================================================
# 8. MEMORY RELEVANCE
# ================================================================
@pytest.mark.asyncio
async def test_p11_memory_relevance_goal(tmp_path):
    mem = MemoryManager(db_path=str(tmp_path / "rel.db"))
    await mem.initialize()
    await mem.create("GOAL", "primary_goal", "Software Engineer at Google")
    await mem.create("STUDY", "last_subject", "Dynamic Programming")
    results = await mem.get_relevant_memories("What is my career goal?", limit=5)
    assert len(results) > 0
    assert any(r["category"] in ["GOAL", "USER_PROFILE"] for r in results)
    await mem.long_term.close()


@pytest.mark.asyncio
async def test_p11_memory_relevance_study(tmp_path):
    mem = MemoryManager(db_path=str(tmp_path / "rel2.db"))
    await mem.initialize()
    await mem.create("STUDY", "last_subject", "DBMS Transactions")
    await mem.create("STUDY", "revision_due", "Graph Algorithms")
    results = await mem.get_relevant_memories("What should I revise?", limit=5)
    assert any(r["category"] == "STUDY" for r in results)
    await mem.long_term.close()


# ================================================================
# 9. CODING OPTIMIZE
# ================================================================
@pytest.mark.asyncio
async def test_p11_coding_optimize_no_code():
    from ai.fallback_provider import FallbackProvider
    tool = CodingTool(FallbackProvider())
    result = await tool.execute({"action": "optimize", "code": "", "language": "python"})
    assert result["success"] is False


@pytest.mark.asyncio
async def test_p11_coding_optimize_with_code():
    from ai.fallback_provider import FallbackProvider
    code = "\nfor i in arr:\n    for j in arr:\n        if arr[i] == arr[j]:\n            pass\n"
    result = await CodingTool(FallbackProvider()).execute({"action": "optimize", "code": code, "language": "python"})
    assert result["success"] is True
    assert len(result["data"]["optimizations"]) > 0
    assert result["data"]["analysis_type"] == "Static AST Structural Inspection (Offline)"


# ================================================================
# 10. SECURITY — NEW TOOLS
# ================================================================
def test_p11_security_rag_low_risk():
    assert RiskClassifier.classify("rag_tool", "query") == RiskLevel.LOW


def test_p11_security_coding_optimize_low_risk():
    assert RiskClassifier.classify("coding_tool", "optimize") == RiskLevel.LOW


# ================================================================
# 11. API INTEGRATION
# ================================================================
@pytest.mark.asyncio
async def test_p11_api_voice_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/voice/transcribe", json={"transcript": ""})
        assert res.status_code == 200
        assert res.json()["success"] is False


@pytest.mark.asyncio
async def test_p11_api_voice_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/voice/transcribe", json={"transcript": "What is my career goal?"})
        assert res.status_code == 200
        d = res.json()
        assert d["success"] is True and d["tts_config"]["text"] == d["response"]


@pytest.mark.asyncio
async def test_p11_api_docs_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.get("/api/documents")
        assert res.status_code == 200 and "documents" in res.json()


@pytest.mark.asyncio
async def test_p11_api_docs_upload_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/documents/upload", json={
            "filename": "test_notes.txt",
            "content": "DBMS Transactions: ACID ensures Atomicity, Consistency, Isolation, Durability in databases.",
            "file_type": "txt"
        })
        assert res.status_code == 200
        assert res.json()["success"] is True and "document_id" in res.json()["data"]


@pytest.mark.asyncio
async def test_p11_api_docs_upload_invalid_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/documents/upload", json={"filename": "malicious.exe", "content": "binary", "file_type": "exe"})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_p11_api_rag_query():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/documents/query", json={"query": "What is normalization?", "top_k": 3})
        assert res.status_code == 200
        assert res.json()["success"] is True and "answer" in res.json()["data"]


@pytest.mark.asyncio
async def test_p11_api_notifications_schedule():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/notifications", json={
            "title": "DBMS Revision", "message": "Review ACID tonight.", "scheduled_for": "2026-09-20T20:00:00"
        })
        assert res.status_code == 200 and res.json()["success"] is True


@pytest.mark.asyncio
async def test_p11_api_notifications_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.get("/api/notifications")
        assert res.status_code == 200 and "notifications" in res.json()


@pytest.mark.asyncio
async def test_p11_api_study_insights():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.get("/api/study/insights")
        assert res.status_code == 200
        d = res.json()
        assert d["success"] is True
        assert "study_streak_days" in d["insights"]
        assert "retention_forecast" in d["insights"]


@pytest.mark.asyncio
async def test_p11_api_memory_relevant():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.get("/api/memory/relevant?q=career+goal&limit=5")
        assert res.status_code == 200
        d = res.json()
        assert d["success"] is True and isinstance(d["memories"], list)


@pytest.mark.asyncio
async def test_p11_api_coding_workspace_optimize():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/coding/workspace", json={
            "action": "optimize",
            "code": "for i in arr:\n    for j in arr:\n        pass",
            "language": "python"
        })
        assert res.status_code == 200 and res.json()["success"] is True


@pytest.mark.asyncio
async def test_p11_api_coding_workspace_invalid_action():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/coding/workspace", json={"action": "execute_shell", "code": "rm -rf /"})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_p11_plan_my_evening():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/chat", json={"message": "Plan my evening"})
        assert res.status_code == 200
        d = res.json()
        assert d["success"] is True and d["intent"] == "SCHEDULE"
        assert "Current time is" in d["response"]


@pytest.mark.asyncio
async def test_p11_rag_query_via_chat():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        res = await c.post("/api/chat", json={"message": "From my DBMS notes, explain normalization"})
        assert res.status_code == 200
        d = res.json()
        assert d["success"] is True and d["intent"] == "RAG_QUERY"
