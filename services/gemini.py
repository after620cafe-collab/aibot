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
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it in Railway Variables.")
        _client = genai.Client(api_key=key)
    return _client

async def ask(prompt: str, system: str | None = None) -> str:
    client = get_client()
    contents = []
    if system:
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=system)]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))

    async with _lock:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=AI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=900,
            ),
        )

    text = getattr(response, "text", None) or "I couldn't generate a reply."
    return text[:MAX_REPLY_CHARS]

async def generate_image(prompt: str):
    client = get_client()
    # Image generation is provider/model dependent. Try Gemini's image-capable
    # response modality first; if unavailable, return a clean error to the bot.
    async with _lock:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation"),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            ),
        )
    return response
