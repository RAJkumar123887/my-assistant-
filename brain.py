"""The assistant's brain: talks to a local Ollama model and remembers each chat."""
import os

import ollama
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful personal assistant. Keep replies short, clear and friendly.",
)
MAX_TURNS = 20  # how many recent exchanges to remember per chat

_histories: dict[str, list[dict]] = {}


def reply(chat_id: str, text: str) -> str:
    """Send one user message to the model and return its answer."""
    history = _histories.setdefault(str(chat_id), [])
    history.append({"role": "user", "content": text})
    del history[: -MAX_TURNS * 2]  # keep only recent messages

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    response = ollama.chat(model=MODEL, messages=messages)
    answer = response["message"]["content"]

    history.append({"role": "assistant", "content": answer})
    return answer


def reset(chat_id: str) -> None:
    """Forget the conversation for this chat."""
    _histories.pop(str(chat_id), None)
