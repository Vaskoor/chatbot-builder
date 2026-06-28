"""
Conversation memory: persists every turn to SQL (per-user, per-bot), and
keeps the prompt efficient on long threads by maintaining a rolling
summary of older turns instead of replaying the entire history every time.
"""

import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.conversation import Conversation, Message
from app.services.llm import fast_completion
from typing import Optional
logger = logging.getLogger(__name__)
def get_or_create_conversation(db: Session, bot_id: str, user_id: str, conversation_id: str | None) -> Conversation:
    if conversation_id:
        convo = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.bot_id == bot_id,
            Conversation.user_id == user_id,
        ).first()
        if convo:
            return convo
    convo = Conversation(bot_id=bot_id, user_id=user_id)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo
def add_message(db: Session, conversation_id: str, role: str, content: str,
                 sources: list | None = None, retrieval_meta: dict | None = None, map_data: Optional[list] = None) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
        retrieval_meta=retrieval_meta,
        map_data=map_data,   # <-- ADD THIS LINE
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if convo and role == "user" and convo.title == "New Conversation":
        convo.title = content[:60] + ("..." if len(content) > 60 else "")
        db.commit()
    return msg
def get_context_window(db: Session, conversation: Conversation) -> str:
    """
    Builds the conversation context to feed the LLM: the rolling summary
    (if one exists) PLUS the most recent N raw turns. This keeps token
    usage bounded even on very long-running conversations while
    preserving long-term continuity ("persistence").
    """
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    recent = messages[-settings.max_recent_turns:]
    parts = []
    if conversation.rolling_summary:
        parts.append(f"[Earlier conversation summary]\n{conversation.rolling_summary}")

    for m in recent:
        role_label = "User" if m.role == "user" else "Assistant"
        parts.append(f"{role_label}: {m.content}")
    return "\n".join(parts)
def maybe_summarize(db: Session, conversation: Conversation):
    """
    If the conversation has grown beyond the configured threshold,
    compress the older portion into a rolling summary and prune it from
    "recent" context (raw messages stay in SQL for history display,
    just not replayed into every LLM call).
    """
    messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
    if len(messages) < settings.summarize_after_turns:
        return
    to_summarize = messages[: -settings.max_recent_turns]
    if not to_summarize:
        return
    transcript = "\n".join(f"{m.role}: {m.content}" for m in to_summarize)
    prompt = (
        "Summarize the following conversation history concisely, preserving any "
        "concrete facts, preferences, names, dates, or decisions the user mentioned "
        "that might matter later. Write 4-8 sentences.\n\n"
        f"{transcript[:6000]}"
    )
    if conversation.rolling_summary:
        prompt += f"\n\nPrevious summary to merge with:\n{conversation.rolling_summary}"
    summary = fast_completion(prompt, system="You are a precise conversation summarizer.", max_tokens=400)
    if summary and "⚠️" not in summary:
        conversation.rolling_summary = summary.strip()
        conversation.summarized_through_message_id = to_summarize[-1].id
        db.commit()
