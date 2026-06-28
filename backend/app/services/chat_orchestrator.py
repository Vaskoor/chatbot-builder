"""
Chat orchestrator: the top-level "brain" of the chatbot. For each user
message it:
  1. Loads/creates the conversation (per-user, per-bot persistence)
  2. Builds efficient conversation context (rolling summary + recent turns)
  3. Runs the retrieval engine (hybrid + rerank + graph escalation)
  4. Builds a grounded prompt and calls the LLM
  5. Persists both turns, runs summarization maintenance, and returns
     a response with full source citations.
"""
import json
import re
import logging
from sqlalchemy.orm import Session
from app.models.bot import Bot
from app.services import memory
from app.services.retrieval import retrieve
from app.services.llm import chat_completion

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = (
    "You are a knowledgeable, helpful assistant. Answer the user's question using "
    "ONLY the provided context when it's relevant. If the context doesn't contain "
    "the answer, say so honestly rather than making things up. Be concise, clear, "
    "and friendly. When context includes conflicting information from different "
    "versions of a document, prefer the most recently updated information." 
)

# Additional instruction to output map data when generating itineraries
MAP_INSTRUCTION = (
    "\n\n**CRITICAL: At the very end of your response, append a JSON block with the exact format:**\n"
    "```json\n"
    "{\n"
    "  \"map_data\": [\n"
    "    {\"day\": 1, \"name\": \"Kathmandu\", \"lat\": 27.7172, \"lng\": 85.3240, \"description\": \"Hotel\"},\n"
    "    {\"day\": 1, \"name\": \"Thamel\", \"lat\": 27.7175, \"lng\": 85.3245, \"description\": \"Dinner\"},\n"
    "    {\"day\": 2, \"name\": \"Pokhara\", \"lat\": 28.2096, \"lng\": 83.9856, \"description\": \"Hotel\"}\n"
    "  ]\n"
    "}\n"
    "```\n"
    "**Important:** Include **every** location mentioned in the itinerary: hotels, restaurants, attractions, viewpoints, and any stop along the way. "
    "Assign a `day` number that matches the day in your itinerary. The order of entries will define the route. "
    "Use realistic coordinates. The JSON must be the final thing in your response."
)

def _build_context_block(chunks: list[dict]) -> str:
    if not chunks:
        return "(No relevant information found in the knowledge base.)"
    lines = []
    for i, c in enumerate(chunks, 1):
        source = c.get("source_file", "unknown")
        truncated = c['text'][:300] + ("..." if len(c['text']) > 300 else "")
        lines.append(f"[{i}] (source: {source})\n{truncated}")
    return "\n\n".join(lines)

def handle_chat(db: Session, bot: Bot, user_id: str, message: str, conversation_id: str | None) -> dict:
    conversation = memory.get_or_create_conversation(db, bot.id, user_id, conversation_id)
    # Persist the user's turn first
    memory.add_message(db, conversation.id, "user", message)

    # Build efficient context (summary + recent turns) BEFORE adding this turn's answer
    conversation_context = memory.get_context_window(db, conversation)

    # Run the retrieval engine
    retrieval_result = retrieve(
        db=db,
        bot_id=bot.id,
        collection_name=bot.chroma_collection_name,
        query=message,
        conversation_context=conversation_context,
    )
    chunks = retrieval_result["chunks"]
    context_block = _build_context_block(chunks)

    system_prompt = bot.system_prompt or DEFAULT_SYSTEM_PROMPT
    # Append the map instruction if the query seems to ask for an itinerary
    # (we can also always include it – it's harmless for non-itinerary queries)
    if any(word in message.lower() for word in ["itinerary", "plan", "trip", "map"]):
        system_prompt += MAP_INSTRUCTION

    llm_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Knowledge base context:\n{context_block}"},
    ]
    if conversation_context:
        llm_messages.append({"role": "system", "content": f"Conversation so far:\n{conversation_context}"})
    llm_messages.append({"role": "user", "content": message})

    answer = chat_completion(llm_messages, temperature=0.4, max_tokens=2048)
        # --- Improved extraction: find the first JSON object containing "map_data" ---
    map_data = None
    start = answer.find('{')
    end = answer.rfind('}')
    if start != -1 and end != -1 and start < end:
        potential_json = answer[start:end+1]
        try:
            data = json.loads(potential_json)
            if 'map_data' in data:
                map_data = data['map_data']
                # Remove the JSON block from the displayed answer
                answer = answer[:start] + answer[end+1:].strip()
                logger.info(f"✅ Extracted map_data (raw): {map_data}")
            else:
                logger.info("ℹ️ JSON found but no 'map_data' key")
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Failed to parse JSON: {e}")
    else:
        logger.info("ℹ️ No JSON object found in answer")

    # Fallback: try to find a code-fenced block if the above fails
    if not map_data:
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', answer, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                map_data = data.get('map_data')
                answer = re.sub(r'```json.*?```', '', answer, flags=re.DOTALL).strip()
                logger.info(f"✅ Extracted map_data from code fence: {map_data}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse JSON from code fence: {e}")

    # Build sources list for the frontend
    sources = [
        {
            "source_file": c.get("source_file"),
            "text_preview": c["text"][:240] + ("..." if len(c["text"]) > 240 else ""),
            "score": round(c.get("rerank_score", c.get("fused_score", 0)), 4),
        }
        for c in chunks
    ]

    # Save the assistant message with sources and map_data
    memory.add_message(
        db, conversation.id, "assistant", answer,
        sources=sources,
        retrieval_meta={
            "strategy": retrieval_result["strategy"],
            "expanded_queries": retrieval_result["expanded_queries"]
        },
        map_data=map_data   # This will be added to the Message model later
    )

    # Best-effort maintenance: compress old history if the thread is getting long
    try:
        memory.maybe_summarize(db, conversation)
    except Exception:
        logger.exception("Conversation summarization failed (non-fatal)")

    return {
        "answer": answer,
        "conversation_id": conversation.id,
        "sources": sources,
        "retrieval_strategy": retrieval_result["strategy"],
        "map_data": map_data,   # include for the API response
    }