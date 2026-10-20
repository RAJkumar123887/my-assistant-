# My AI Assistant

A free, private AI assistant that runs on your own computer using
[Ollama](https://ollama.com). No API keys or paid AI services needed.

**What works now**
- Terminal chat (`terminal_chat.py`)
- Telegram bot (`telegram_bot.py`)

**Planned next:** WhatsApp / Instagram replies, then voice calls.

## 1. Setup

1. Install Python 3.10+ and [Ollama](https://ollama.com/download).
2. Download a model (small and fast):
   ```
   ollama pull llama3.2
   ```
3. Install the project:
   ```
   pip install -r requirements.txt
   ```
4. Create your settings file:
   ```
   cp .env.example .env
   ```

## 2. Test the brain in the terminal

```
python terminal_chat.py
```

## 3. Connect Telegram

1. In Telegram, message **@BotFather**, send `/newbot`, and follow the steps.
2. Copy the token it gives you into `.env` as `TELEGRAM_BOT_TOKEN`.
3. Message **@userinfobot** to get your user ID, and put it in `ALLOWED_USER_IDS`
   so only you can use the bot.
4. Run:
   ```
   python telegram_bot.py
   ```
5. Open your bot in Telegram and say hi.

Your computer must stay on, with Ollama running, for the bot to reply.

## 4. Put it on GitHub

```
git init
git add .
git commit -m "My AI assistant"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/my-assistant.git
git push -u origin main
```

`.env` is in `.gitignore`, so your bot token is never uploaded. Never remove that.

## Run it fully inside GitHub (no PC needed)

`github_bot.py` + `.github/workflows/telegram-bot.yml` run the Telegram bot on
GitHub Actions, using the free GitHub Models AI.

1. Push this project to a **public** GitHub repo (private repos only get 2,000
   free minutes a month, which this uses up in about 1.5 days).
2. Repo > Settings > Secrets and variables > Actions > **Secrets**, add:
   - `TELEGRAM_BOT_TOKEN` (from @BotFather)
   - `ALLOWED_USER_IDS` (your Telegram ID, so strangers can't use your bot)
3. Optional: under **Variables**, add `MODEL` (default is `openai/gpt-4o-mini`).
4. Go to the **Actions** tab, enable workflows, open "Telegram assistant" and
   click **Run workflow**. After that it restarts itself every 5 minutes.

Limits: replies can be delayed or missed for a few minutes when GitHub is busy,
memory resets between runs, and GitHub Models has free rate limits.

## Roadmap

| Step | Feature | Tools |
|------|---------|-------|
| 1 | Telegram + terminal (done) | Ollama, python-telegram-bot |
| 2 | WhatsApp / Instagram replies | Meta Cloud API (official, needs a business account) |
| 3 | Voice calls | Twilio/Exotel + Whisper (speech-to-text) + Piper (text-to-speech) + Pipecat |

## Notes

- Use official APIs only. Automating personal social accounts gets them banned.
- Calling people with an AI is regulated in India (TRAI rules). Only call people who agreed to it.
- If replies are slow, use a smaller model (`llama3.2:1b`) or a computer with a GPU.
