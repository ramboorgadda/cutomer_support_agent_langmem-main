from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from customer_support_agent.api.dependencies import (
    get_copilot,
    get_draft_service,
    get_drafts_repository,
    get_tickets_repository,
)
from customer_support_agent.repositories.sqlite.drafts import DraftsRepository
from customer_support_agent.repositories.sqlite.tickets import TicketsRepository
from customer_support_agent.schemas.api import DraftResponse, DraftUpdateRequest
from customer_support_agent.services.draft_service import DraftService