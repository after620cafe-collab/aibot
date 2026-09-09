# Rani AI V3

Professional Discord all-rounder bot made by Tyson.

## Railway Variables
Required:
- DISCORD_TOKEN
- GROQ_API_KEY

Optional:
- GROQ_MODEL=openai/gpt-oss-20b
- PREFIX=-
- AI_AUTO_CHANNEL_ID=
- TTS_VOICE=hi-IN-SwaraNeural

## Main commands
- -help
- -ai <message>
- /ai <message>
- -translate <language> <text>
- -joinvc / -leavevc
- -t <text> (Hindi TTS in VC)
- -nitro (safe prank)
- -ban / -unban / -kick / -mute / -unmute
- -unbanall confirm
- -unmuteall confirm
- -clear / -lock / -unlock / -hide / -unhide / -slowmode / -clone / -snipe
- -warn / -warnings / -clearwarns
- -voicekick / -voicemute / -voiceunmute / -vcmove / -vcpull
- -vcdeafen / -vcundeafen / -voiceban / -voiceunban
- -autoresponder
- -tagreaction
- -createrole / -giverole / -removerole / -rolecolor
- -8ball / -coinflip / -dice / -rps / -joke / -truth / -dare

Image generation was intentionally removed.
## Music
Rani includes a YouTube music player using yt-dlp + FFmpeg.

Commands:
- `-play <song name or YouTube URL>`
- `-pause`, `-resume`, `-skip`, `-stop`
- `-queue`, `-nowplaying`, `-shuffle`, `-remove <number>`
- `-loop off|track|queue`
- `-volume 1-200`
- `-247 on|off`
- `-joinmusic`, `-leavemusic`, `-musichelp`

`-247 on` keeps Rani connected and repeats the last track when the queue becomes empty. It also uses reconnect flags for stream interruptions. No Discord bot can guarantee 100% uptime if the host, Discord, or source service goes down.


**Bot:** Rani AI  
**Created by:** Tyson
