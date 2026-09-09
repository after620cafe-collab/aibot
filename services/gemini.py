import os
import asyncio
from google import genai
from google.genai import types
from config import AI_MODEL, MAX_REPLY_CHARS

_client = None
_lock = asyncio.Lock()


def get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing in Railway Variables")
        _client = genai.Client(api_key=key)
    return _client


def friendly_error(exc: Exception) -> str:
    text = str(exc).replace("\n", " ")
    low = text.lower()
    if "api key" in low or "unauthenticated" in low or "401" in low or "403" in low:
        return "Gemini API key is invalid/not authorized. Create a fresh Gemini API key and replace `GEMINI_API_KEY` in Railway."
    if "quota" in low or "429" in low or "resource exhausted" in low:
        return "Gemini rate limit/quota reached. Try again in a little while."
    if "not found" in low or "404" in low:
        return f"Gemini model `{AI_MODEL}` was not found/available for this key."
    return f"Gemini request failed: {type(exc).__name__}. Check Railway deployment logs."


async def ask(prompt: str) -> str:
    client = get_client()
    async with _lock:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=AI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                max_output_tokens=900,
            ),
        )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text[:MAX_REPLY_CHARS]


async def generate_image(prompt: str):
    client = get_client()
    model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    async with _lock:
        return await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
