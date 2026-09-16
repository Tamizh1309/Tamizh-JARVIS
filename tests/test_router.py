import pytest
from ai.fallback_provider import FallbackProvider
from core.router import IntentRouter


@pytest.mark.asyncio
async def test_intent_router_next_best_action():
    provider = FallbackProvider()
    router = IntentRouter(provider)
    intent, conf, entities = await router.route("What should I study now?")
    assert intent == "NEXT_BEST_ACTION"
    assert conf >= 0.8


@pytest.mark.asyncio
async def test_intent_router_task_create():
    provider = FallbackProvider()
    router = IntentRouter(provider)
    intent, conf, entities = await router.route("create task: Complete GATE CS Quiz 2")
    assert intent == "TASK_CREATE"
    assert "GATE CS Quiz 2" in entities.get("title", "")


@pytest.mark.asyncio
async def test_intent_router_daily_briefing():
    provider = FallbackProvider()
    router = IntentRouter(provider)
    intent, conf, entities = await router.route("Give me today's daily briefing")
    assert intent == "DAILY_BRIEFING"


@pytest.mark.asyncio
async def test_intent_router_general_chat():
    provider = FallbackProvider()
    router = IntentRouter(provider)
    intent, conf, entities = await router.route("Hello there")
    assert intent == "GENERAL_CHAT"
