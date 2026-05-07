from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from customer_support_agent.api.routers import (
    drafts_router,
    health_router,
    knowledge_router,
    memory_router,
    tickets_router,
)
from customer_support_agent.core.settings import Settings, ensure_directories, get_settings
from customer_support_agent.repositories.sqlite import init_db