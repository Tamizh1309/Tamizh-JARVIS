import sys
from pathlib import Path
import pytest_asyncio

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import api.chat


@pytest_asyncio.fixture(autouse=True)
async def cleanup_core_connection():
    yield
    if api.chat._core_instance and hasattr(api.chat._core_instance, "memory") and api.chat._core_instance.memory:
        try:
            await api.chat._core_instance.memory.long_term.close()
        except Exception:
            pass
