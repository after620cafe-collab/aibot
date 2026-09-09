import os
PREFIX = os.getenv("PREFIX", "-")
AI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", "12"))
MAX_REPLY_CHARS = 1900
