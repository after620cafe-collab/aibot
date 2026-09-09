# Aqua AI — Discord All-Rounder Bot

Prefix: `-`

## Features

- AI chat with Gemini
- Conversation memory
- Mention-based AI replies
- Translation / rewriting / summarization
- AI roast and rizz
- Fun games
- Moderation commands
- Image-generation command (only if the configured Gemini model/account supports image output)
- Discord VC join/leave foundation
- Railway-ready start command
- Secrets kept outside GitHub

## 1. Discord setup

Create a bot in the Discord Developer Portal.

Enable these **Privileged Gateway Intents**:
- Message Content Intent
- Server Members Intent
- Presence Intent

Invite it with `bot` and `applications.commands` scopes.

## 2. Google Gemini API key

Create a Gemini API key in Google AI Studio.

Put the key only in Railway Variables as `GEMINI_API_KEY`.

## 3. GitHub

Upload all project files.

Do NOT upload `.env`.
Only `.env.example` should be committed.

## 4. Railway

Create a Railway project and deploy this GitHub repository.

Variables:

DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
PREFIX=-

Optional:

GEMINI_MODEL=gemini-2.5-flash
MAX_MEMORY_MESSAGES=12
AI_AUTO_CHANNEL_ID=

The repository already includes `railway.toml` with:

python main.py

## 5. Test

- `-ping`
- `-help`
- `-ai hello`
- `-translate hindi How are you?`
- `-rewrite professional send me the file`
- `-joke`
- `-rizz coffee is my favorite`
- `-roast @user`
- `-coinflip`
- `-dice`
- `-joinvc`

## Important

Free API limits can change. Image generation and voice AI are provider/Discord dependency dependent. The bot catches these failures instead of intentionally crashing.

Never share your Discord token or API key.
