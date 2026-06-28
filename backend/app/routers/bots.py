import re
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.document import Document, Chunk
from app.schemas.bot import BotCreate, BotUpdate, BotOut
from app.services.vector_store import delete_collection
router = APIRouter(prefix="/api/bots", tags=["bots"])
def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "bot"
def _to_bot_out(bot: Bot, db: Session) -> BotOut:
    doc_count = db.query(Document).filter(Document.bot_id == bot.id, Document.is_latest == True).count()
    chunk_count = db.query(Chunk).filter(Chunk.bot_id == bot.id, Chunk.is_active == True).count()
    out = BotOut.model_validate(bot)
    out.document_count = doc_count
    out.chunk_count = chunk_count
    return out
@router.post("", response_model=BotOut)
def create_bot(payload: BotCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    collection_name = f"bot_{_slugify(payload.name)}_{uuid.uuid4().hex[:8]}"
    bot = Bot(
        owner_id=user.id,
        name=payload.name,
        description=payload.description,
        system_prompt=payload.system_prompt,
        chroma_collection_name=collection_name,
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return _to_bot_out(bot, db)
@router.get("", response_model=list[BotOut])
def list_bots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bots = db.query(Bot).filter(Bot.owner_id == user.id).order_by(Bot.created_at.desc()).all()
    return [_to_bot_out(b, db) for b in bots]
def _get_owned_bot(db: Session, bot_id: str, user: User) -> Bot:
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.owner_id == user.id).first()
    if not bot:
        raise HTTPException(404, "Bot not found")
    return bot
@router.get("/{bot_id}", response_model=BotOut)
def get_bot(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    return _to_bot_out(bot, db)
@router.patch("/{bot_id}", response_model=BotOut)
def update_bot(bot_id: str, payload: BotUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    if payload.name is not None:
        bot.name = payload.name
    if payload.description is not None:
        bot.description = payload.description
    if payload.system_prompt is not None:
        bot.system_prompt = payload.system_prompt
    db.commit()
    db.refresh(bot)
    return _to_bot_out(bot, db)
@router.delete("/{bot_id}")
def delete_bot(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    delete_collection(bot.chroma_collection_name)
    db.delete(bot)
    db.commit()
    return {"success": True}
