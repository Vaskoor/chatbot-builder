"""
Groq LLM client wrapper. Provides both a 'fast' small model (for cheap
internal steps like query expansion/HyDE/entity extraction) and the
main quality model for final answer generation.
"""
from groq import Groq
from app.core.config import settings
import json
import logging
logger = logging.getLogger(__name__)
_client = None
def get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Please add it to your .env file.")
        _client = Groq(api_key=settings.groq_api_key)
    return _client
def chat_completion(

    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 1024,
    json_mode: bool = False,
) -> str:
    """
    Generic chat completion call. messages = [{"role": "user"/"system"/"assistant", "content": "..."}]
    """
    if not settings.groq_api_key:
        return "⚠️ GROQ_API_KEY not set. Please configure it in your .env file to enable chat responses."
    client = get_client()
    kwargs = dict(
        model=model or settings.groq_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:
        logger.exception("Groq API call failed")
        return f"⚠️ LLM request failed: {str(e)}"
def fast_completion(prompt: str, system: str = "", max_tokens: int = 256) -> str:
    """Cheap/fast call using the smaller model — used for query expansion, HyDE, entity extraction."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat_completion(messages, model=settings.groq_fast_model, temperature=0.2, max_tokens=max_tokens)
def fast_json_completion(prompt: str, system: str = "", max_tokens: int = 512) -> dict:
    """Fast call that expects a JSON object back. Returns {} on parse failure."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    raw = chat_completion(messages, model=settings.groq_fast_model, temperature=0.1,
                           max_tokens=max_tokens, json_mode=True)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse JSON from fast_json_completion: %s", raw[:200] if raw else raw)
        return {}
