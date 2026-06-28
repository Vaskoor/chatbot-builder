from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, ChatResponse, ConversationOut, ConversationDetail
from app.services.chat_orchestrator import handle_chat
from app.routers.bots import _get_owned_bot
router = APIRouter(prefix="/api/bots/{bot_id}", tags=["chat"])
@router.post("/chat", response_model=ChatResponse)
def chat(bot_id: str, payload: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    result = handle_chat(db, bot, user.id, payload.message, payload.conversation_id)
    return ChatResponse(**result)
@router.get("/conversations", response_model=List[ConversationOut])
def list_conversations(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    convos = (
        db.query(Conversation)
        .filter(Conversation.bot_id == bot.id, Conversation.user_id == user.id)
        .order_by(desc(Conversation.updated_at))
        .all()
    )
    return convos
@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(bot_id: str, conversation_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.bot_id == bot.id, Conversation.user_id == user.id
    ).first()
    if not convo:
        raise HTTPException(404, "Conversation not found")
    return convo
@router.delete("/conversations/{conversation_id}")
def delete_conversation(bot_id: str, conversation_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id, Conversation.bot_id == bot.id, Conversation.user_id == user.id
    ).first()
    if not convo:
        raise HTTPException(404, "Conversation not found")
    db.delete(convo)
    db.commit()
    return {"success": True}
