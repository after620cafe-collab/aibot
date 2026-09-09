import os
import asyncio
from groq import Groq
from config import AI_MODEL, MAX_REPLY_CHARS

_client = None

def get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            raise RuntimeError("GROQ_API_KEY is missing in Railway Variables.")
        _client = Groq(api_key=key)
    return _client

def friendly_error(exc):
    text = str(exc).replace("\n", " ")
    low = text.lower()
    if "401" in low or "authentication" in low or "invalid api key" in low:
        return "Groq API key is invalid. Create a fresh key and update `GROQ_API_KEY` in Railway."
    if "429" in low or "rate limit" in low:
        return "Groq free-tier rate limit reached. Wait a little and try again."
    if "model" in low and ("not found" in low or "does not exist" in low):
        return f"Groq model `{AI_MODEL}` is unavailable. Use `openai/gpt-oss-20b`."
    return f"AI request failed: {type(exc).__name__}. Check Railway logs."

async def ask(messages):
    client = get_client()
    def run():
        return client.chat.completions.create(
            model=AI_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=900,
        )
    response = await asyncio.to_thread(run)
    text = response.choices[0].message.content if response.choices else ""
    if not text:
        raise RuntimeError("AI returned an empty response.")
    return text[:MAX_REPLY_CHARS]
