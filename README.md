# Rani Discord Bot — Railway Ready

This build has **AI/Groq removed**. Prefix and slash commands use the same hybrid command implementation.

## Railway Variables
- `DISCORD_TOKEN` = your Discord bot token
- `PREFIX` = `-`
- `SYNC_GUILD_ID` = your server ID for instant slash-command sync (recommended)
- `TTS_VOICE` = `hi-IN-SwaraNeural` (optional)

## Discord Developer Portal
Enable **Message Content Intent** and **Server Members Intent**. When inviting the bot, include both `bot` and `applications.commands` scopes.

## Music
The bot uses yt-dlp + Deno EJS support + FFmpeg. Join a voice channel and use either:
- `-play song name`
- `/play song name`

The same applies to music controls and the other bot commands.
