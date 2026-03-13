from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional
from app.services.ai import chat_with_ai
from app.database import get_session
from app.models import Conversation, Document
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    document_id: Optional[int] = None

@router.post("/")
def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    document_context = None

    if request.document_id:
        document = session.exec(
            select(Document).where(
                Document.id == request.document_id,
                Document.user_id == current_user.id
            )
        ).first()
        if document:
            document_context = document.content

    assistant_message = chat_with_ai(
        request.message,
        request.history,
        document_context
    )

    conversation = Conversation(
        user_id=current_user.id,
        user_message=request.message,
        ai_response=assistant_message
    )
    session.add(conversation)
    session.commit()

    updated_history = request.history + [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": assistant_message}
    ]

    return {
        "response": assistant_message,
        "history": updated_history
    }

@router.get("/history")
def get_history(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    conversations = session.exec(
        select(Conversation).where(Conversation.user_id == current_user.id)
    ).all()
    return conversations