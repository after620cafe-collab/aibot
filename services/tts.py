import os
import asyncio
import edge_tts

VOICE = os.getenv("TTS_VOICE", "hi-IN-SwaraNeural")

async def synthesize(text, out_path):
    text = text.strip()[:2000]
    if not text:
        raise ValueError("TTS text is empty.")
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(out_path)

async def synthesize_safe(text, out_path):
    try:
        await synthesize(text, out_path)
        return out_path
    except Exception:
        # English fallback if the configured Hindi voice is unavailable.
        fallback = "en-IN-NeerjaNeural"
        communicate = edge_tts.Communicate(text[:2000], fallback)
        await communicate.save(out_path)
        return out_path
