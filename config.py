import os

PREFIX = os.getenv("PREFIX", "-")
AI_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", "12"))
MAX_REPLY_CHARS = 1900
