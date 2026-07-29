"""
Chat API Router

POST /chat → Accept user question, return response
             (Currently placeholder — AI integration pending for Stage 3)
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="AI Chat endpoint",
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    POST /chat: Accept a user question and return a response.

    Currently returns a placeholder response.
    In Stage 3, this endpoint will be connected to the AI provider
    which will use function/tool calling to query PostgreSQL
    via the service layer.
    """
    logger.info(f"POST /chat — question='{request.question[:80]}...'")
    return handle_chat(db, request)
