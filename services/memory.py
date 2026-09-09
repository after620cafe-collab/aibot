from collections import defaultdict, deque
from config import MAX_MEMORY_MESSAGES

_memory = defaultdict(lambda: deque(maxlen=MAX_MEMORY_MESSAGES))

def add(key: str, role: str, text: str):
    _memory[key].append((role, text))

def get(key: str):
    return list(_memory[key])

def clear(key: str):
    _memory.pop(key, None)

def format_history(key: str) -> str:
    rows = []
    for role, text in get(key):
        rows.append(f"{role}: {text}")
    return "\n".join(rows)
