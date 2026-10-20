"""Telegram assistant that runs entirely inside GitHub Actions.

Uses GitHub Models (free tier) as the brain, so no API key or local PC is needed.
Each workflow run listens to Telegram for ~4.5 minutes, then the next run takes over.
Only the Python standard library is used.
"""
import json
import os
import time
import urllib.error
import urllib.request

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
MODEL = os.getenv("MODEL") or "openai/gpt-4o-mini"
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT") or (
    "You are a helpful personal assistant. Keep replies short, clear and friendly."
)
ALLOWED = {u.strip() for u in os.getenv("ALLOWED_USER_IDS", "").split(",") if u.strip()}
RUN_SECONDS = int(os.getenv("RUN_SECONDS") or 270)
MAX_MESSAGES = 20

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
MODELS_URL = "https://models.github.ai/inference/chat/completions"

histories: dict[int, list[dict]] = {}  # memory lasts only while this run is active


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def ask_model(chat_id: int, text: str) -> str:
    history = histories.setdefault(chat_id, [])
    history.append({"role": "user", "content": text})
    del history[:-MAX_MESSAGES]
    data = post_json(
        MODELS_URL,
        {
            "model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history,
        },
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
    )
    answer = data["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": answer})
    return answer


def send(chat_id: int, text: str) -> None:
    post_json(f"{TG}/sendMessage", {"chat_id": chat_id, "text": text[:4000]})


def handle(message: dict) -> None:
    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text")
    if not text:
        return
    if ALLOWED and user_id not in ALLOWED:
        send(chat_id, "Sorry, you are not allowed to use this bot.")
        return
    if text.startswith("/start"):
        send(chat_id, "Hi! I'm your assistant. Send me a message. /reset clears my memory.")
        return
    if text.startswith("/reset"):
        histories.pop(chat_id, None)
        send(chat_id, "Memory cleared.")
        return
    try:
        send(chat_id, ask_model(chat_id, text))
    except urllib.error.HTTPError as e:
        send(chat_id, f"AI error {e.code}: {e.read().decode()[:300]}")
    except Exception as e:  # keep the bot alive on any failure
        send(chat_id, f"Something went wrong: {e}")


def main() -> None:
    offset = None
    deadline = time.time() + RUN_SECONDS
    print(f"Listening for about {RUN_SECONDS}s with model {MODEL}")
    while time.time() < deadline:
        payload = {"timeout": 20, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        try:
            result = post_json(f"{TG}/getUpdates", payload, timeout=40)
        except Exception as e:
            print("getUpdates failed:", e)
            time.sleep(3)
            continue
        for update in result.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update:
                handle(update["message"])
    if offset is not None:  # confirm processed messages so they are not repeated
        try:
            post_json(f"{TG}/getUpdates", {"offset": offset, "timeout": 0})
        except Exception:
            pass
    print("Run finished.")


if __name__ == "__main__":
    main()
