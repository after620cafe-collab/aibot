from collections import defaultdict, deque
from config import MAX_MEMORY_MESSAGES

_memory = defaultdict(lambda: deque(maxlen=MAX_MEMORY_MESSAGES))

def add(key, role, content):
    _memory[key].append((role, content))

def clear(key):
    _memory.pop(key, None)

def format_history(key):
    rows = _memory.get(key, ())
    return "\n".join(f"{role}: {content}" for role, content in rows)
