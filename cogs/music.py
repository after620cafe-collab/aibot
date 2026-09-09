import asyncio
import random
from dataclasses import dataclass, field
from typing import Optional

import discord
from discord.ext import commands
import yt_dlp

from config import PREFIX

RED = discord.Color.from_rgb(220, 35, 55)

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "ignoreerrors": False,
    "remote_components": "ejs:github",
    "extractor_args": {
        "youtube": {
            "player_client": ["default"],
        }
    },
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
    "options": "-vn -ac 2 -ar 48000 -b:a 192k -bufsize 512k",
}

YTDL = yt_dlp.YoutubeDL(YTDL_OPTIONS)


@dataclass
class Track:
    title: str
    url: str
    webpage: str
    duration: int = 0
    requester: str = ""
    thumbnail: str = ""


@dataclass
class GuildMusic:
    queue: list[Track] = field(default_factory=list)
    current: Optional[Track] = None
    voice: Optional[discord.VoiceClient] = None
    volume: float = 1.0
    loop: str = "off"  # off, track, queue
    stay_24_7: bool = False
    text_channel: Optional[discord.TextChannel] = None
    play_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def fmt_time(seconds: int) -> str:
    if not seconds:
        return "LIVE"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


class MusicButtons(discord.ui.View):
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id

    async def action(self, interaction, action_name):
        await interaction.response.defer()
        state = self.cog.states.get(self.guild_id)
        if not state or not state.voice:
            return await interaction.followup.send("❌ Rani is not in a voice channel.", ephemeral=True)

        vc = state.voice
        if action_name == "pause":
            if vc.is_playing():
                vc.pause()
                return await interaction.followup.send("⏸️ Paused.", ephemeral=True)
        elif action_name == "resume":
            if vc.is_paused():
                vc.resume()
                return await interaction.followup.send("▶️ Resumed.", ephemeral=True)
        elif action_name == "skip":
            if vc.is_playing() or vc.is_paused():
                vc.stop()
                return await interaction.followup.send("⏭️ Skipping...", ephemeral=True)
        elif action_name == "stop":
            state.queue.clear()
            state.loop = "off"
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            state.current = None
            return await interaction.followup.send("⏹️ Stopped and cleared the queue.", ephemeral=True)
        elif action_name == "queue":
            return await self.cog.send_queue(interaction.followup, state)
        await interaction.followup.send("ℹ️ Nothing to do right now.", ephemeral=True)

    @discord.ui.button(label="Pause", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        await self.action(interaction, "pause")

    @discord.ui.button(label="Resume", emoji="▶️", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        await self.action(interaction, "resume")

    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        await self.action(interaction, "skip")

    @discord.ui.button(label="Queue", emoji="📜", style=discord.ButtonStyle.secondary)
    async def queue(self, interaction, button):
        await self.action(interaction, "queue")

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction, button):
        await self.action(interaction, "stop")


class Music(commands.Cog):
    """Rani's high-quality YouTube music player."""

    def __init__(self, bot):
        self.bot = bot
        self.states: dict[int, GuildMusic] = {}
        self.tasks: set[asyncio.Task] = set()

    def state(self, guild_id: int) -> GuildMusic:
        return self.states.setdefault(guild_id, GuildMusic())

    async def extract(self, query: str) -> Track:
        def run():
            target = query
            if not query.startswith(("http://", "https://")):
                target = f"ytsearch1:{query}"
            data = YTDL.extract_info(target, download=False)
            if not data:
                raise RuntimeError("No result found.")
            if "entries" in data:
                entries = [e for e in data["entries"] if e]
                if not entries:
                    raise RuntimeError("No result found.")
                data = entries[0]
            return Track(
                title=data.get("title") or "Unknown track",
                url=data.get("url"),
                webpage=data.get("webpage_url") or data.get("original_url") or "",
                duration=int(data.get("duration") or 0),
                requester="",
                thumbnail=data.get("thumbnail") or "",
            )
        return await asyncio.wait_for(asyncio.to_thread(run), timeout=35)

    async def ensure_voice(self, ctx) -> Optional[discord.VoiceClient]:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("🎙️ Pehle kisi voice channel me join ho jao.", mention_author=False)
            return None

        channel = ctx.author.voice.channel
        state = self.state(ctx.guild.id)

        if ctx.guild.voice_client:
            vc = ctx.guild.voice_client
            state.voice = vc
            if vc.channel.id != channel.id and not vc.is_playing():
                await vc.move_to(channel)
            return vc

        try:
            vc = await channel.connect(self_deaf=True)
            state.voice = vc
            return vc
        except Exception as e:
            await ctx.reply(f"❌ Voice join failed: `{type(e).__name__}`", mention_author=False)
            return None

    def player_embed(self, track: Track, state: GuildMusic) -> discord.Embed:
        e = discord.Embed(
            title="🔴 RANI MUSIC • NOW PLAYING",
            description=f"**[{track.title}]({track.webpage})**",
            color=RED,
        )
        e.add_field(name="⏱️ Duration", value=fmt_time(track.duration), inline=True)
        e.add_field(name="🔊 Volume", value=f"{round(state.volume * 100)}%", inline=True)
        e.add_field(name="🔁 Loop", value=state.loop.upper(), inline=True)
        if track.requester:
            e.add_field(name="👤 Requested by", value=track.requester, inline=True)
        if state.stay_24_7:
            e.add_field(name="♾️ 24/7", value="ON", inline=True)
        if track.thumbnail:
            e.set_thumbnail(url=track.thumbnail)
        e.set_footer(text="Rani Music • Made by Tyson")
        return e

    async def play_next(self, guild_id: int):
        state = self.state(guild_id)
        async with state.play_lock:
            vc = state.voice
            if not vc or not vc.is_connected():
                return

            if state.loop == "track" and state.current:
                track = state.current
            elif state.queue:
                track = state.queue.pop(0)
            elif state.loop == "queue" and state.current:
                track = state.current
            elif state.stay_24_7 and state.current:
                # 24/7 mode keeps the last song playing instead of going silent.
                track = state.current
            else:
                state.current = None
                return

            state.current = track

            try:
                fresh = await self.extract(track.webpage or track.title)
                track.url = fresh.url
                if fresh.webpage:
                    track.webpage = fresh.webpage
                if fresh.thumbnail:
                    track.thumbnail = fresh.thumbnail
            except Exception:
                fresh = track

            def after(error):
                if error:
                    print(f"[Music] playback error in {guild_id}: {error}")
                task = asyncio.run_coroutine_threadsafe(self.play_next(guild_id), self.bot.loop)
                self.tasks.add(task)
                task.add_done_callback(self.tasks.discard)

            try:
                source = discord.FFmpegOpusAudio(
                    fresh.url,
                    before_options=FFMPEG_OPTIONS["before_options"],
                    options=FFMPEG_OPTIONS["options"],
                )
                source = discord.PCMVolumeTransformer(source, volume=state.volume)
                vc.play(source, after=after)
                if state.text_channel:
                    try:
                        await state.text_channel.send(
                            embed=self.player_embed(track, state),
                            view=MusicButtons(self, guild_id),
                        )
                    except Exception:
                        pass
            except Exception as e:
                if state.text_channel:
                    await state.text_channel.send(
                        f"⚠️ **Playback error:** `{str(e)[:500]}`\\nTrying the next track..."
                    )
                asyncio.create_task(self.play_next(guild_id))

    async def send_queue(self, destination, state: GuildMusic):
        e = discord.Embed(title="🔴 RANI MUSIC • QUEUE", color=RED)
        if state.current:
            e.add_field(name="🎵 Now", value=f"**{state.current.title}**", inline=False)
        if state.queue:
            lines = [f"`{i}.` {t.title}" for i, t in enumerate(state.queue[:15], 1)]
            extra = len(state.queue) - len(lines)
            text = "\n".join(lines)
            if extra > 0:
                text += f"\n…and **{extra}** more."
            e.add_field(name="📜 Up Next", value=text, inline=False)
        else:
            e.add_field(name="📜 Up Next", value="Queue is empty.", inline=False)
        e.set_footer(text=f"Loop: {state.loop.upper()} • 24/7: {'ON' if state.stay_24_7 else 'OFF'} • Made by Tyson")
        return await destination.send(embed=e)

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        """Play a song name or YouTube URL."""
        if not ctx.guild:
            return
        vc = await self.ensure_voice(ctx)
        if not vc:
            return
        state = self.state(ctx.guild.id)
        state.text_channel = ctx.channel

        msg = await ctx.reply("🔎 **Rani is searching...**", mention_author=False)
        try:
            track = await self.extract(query)
            track.requester = ctx.author.display_name
            if vc.is_playing() or vc.is_paused():
                state.queue.append(track)
                await msg.edit(content=f"➕ **Added to queue:** `{track.title}`")
            else:
                state.queue.insert(0, track)
                await msg.edit(content=f"🎵 **Loading:** `{track.title}`")
                await self.play_next(ctx.guild.id)
        except asyncio.TimeoutError:
            await msg.edit(content="❌ YouTube took too long to respond. Please try the song again in a few seconds.")
        except Exception as e:
            error_text = str(e).replace("\\n", " ")[:700]
            await msg.edit(content=f"❌ **Music error:** `{error_text or type(e).__name__}`")

    @commands.command(name="pause")
    async def pause_cmd(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.reply("⏸️ **Paused.**", mention_author=False)
        else:
            await ctx.reply("❌ Nothing is playing.", mention_author=False)

    @commands.command(name="resume", aliases=["unpause"])
    async def resume_cmd(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.reply("▶️ **Resumed.**", mention_author=False)
        else:
            await ctx.reply("❌ Nothing is paused.", mention_author=False)

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        vc = ctx.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await ctx.reply("⏭️ **Skipped.**", mention_author=False)
        else:
            await ctx.reply("❌ Nothing is playing.", mention_author=False)

    @commands.command(name="stop", aliases=["disconnect"])
    async def stop(self, ctx):
        state = self.state(ctx.guild.id)
        state.queue.clear()
        state.current = None
        state.loop = "off"
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect(force=True)
        state.voice = None
        await ctx.reply("⏹️ **Music stopped and queue cleared.**", mention_author=False)

    @commands.command(name="queue", aliases=["q"])
    async def queue_cmd(self, ctx):
        await self.send_queue(ctx, self.state(ctx.guild.id))

    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        state = self.state(ctx.guild.id)
        if not state.current:
            return await ctx.reply("❌ Nothing is playing.", mention_author=False)
        await ctx.reply(embed=self.player_embed(state.current, state), view=MusicButtons(self, ctx.guild.id), mention_author=False)

    @commands.command(name="volume", aliases=["vol"])
    @commands.has_permissions(manage_guild=True)
    async def volume(self, ctx, level: int):
        if not 1 <= level <= 200:
            return await ctx.reply("🔊 Volume must be between **1 and 200**.", mention_author=False)
        state = self.state(ctx.guild.id)
        state.volume = level / 100
        vc = ctx.guild.voice_client
        if vc and getattr(vc, "source", None) and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = state.volume
        await ctx.reply(f"🔊 Volume set to **{level}%**.", mention_author=False)

    @commands.command(name="loop")
    async def loop_cmd(self, ctx, mode: str = "track"):
        mode = mode.lower()
        if mode not in ("off", "track", "queue"):
            return await ctx.reply("🔁 Use `-loop off`, `-loop track`, or `-loop queue`.", mention_author=False)
        state = self.state(ctx.guild.id)
        state.loop = mode
        await ctx.reply(f"🔁 Loop mode: **{mode.upper()}**", mention_author=False)

    @commands.command(name="247", aliases=["24/7", "stay"])
    async def always_on(self, ctx, mode: str = "on"):
        mode = mode.lower()
        if mode not in ("on", "off"):
            return await ctx.reply("♾️ Use `-247 on` or `-247 off`.", mention_author=False)
        state = self.state(ctx.guild.id)
        state.stay_24_7 = mode == "on"
        if state.stay_24_7:
            state.loop = "track"
            await ctx.reply("♾️ **24/7 mode ON.** Rani will keep the last song playing and reconnect when possible.", mention_author=False)
        else:
            await ctx.reply("♾️ **24/7 mode OFF.**", mention_author=False)

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        state = self.state(ctx.guild.id)
        if len(state.queue) < 2:
            return await ctx.reply("🔀 Need at least 2 queued songs.", mention_author=False)
        random.shuffle(state.queue)
        await ctx.reply("🔀 **Queue shuffled.**", mention_author=False)

    @commands.command(name="remove")
    async def remove(self, ctx, position: int):
        state = self.state(ctx.guild.id)
        if position < 1 or position > len(state.queue):
            return await ctx.reply("❌ Invalid queue position.", mention_author=False)
        track = state.queue.pop(position - 1)
        await ctx.reply(f"🗑️ Removed **{track.title}**.", mention_author=False)

    @commands.command(name="joinmusic", aliases=["joinvc", "musicjoin"])
    async def join_music(self, ctx):
        vc = await self.ensure_voice(ctx)
        if vc:
            self.state(ctx.guild.id).text_channel = ctx.channel
            await ctx.reply(f"🎧 **Rani joined:** `{vc.channel.name}`", mention_author=False)

    @commands.command(name="leavemusic", aliases=["leavevc", "musicleave"])
    async def leave_music(self, ctx):
        state = self.state(ctx.guild.id)
        state.stay_24_7 = False
        state.queue.clear()
        state.current = None
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect(force=True)
        state.voice = None
        await ctx.reply("👋 **Rani left the voice channel.**", mention_author=False)


    async def _slash_ctx(self, interaction: discord.Interaction):
        class Ctx:
            guild = interaction.guild
            author = interaction.user
            channel = interaction.channel
            voice_client = interaction.guild.voice_client if interaction.guild else None
            async def reply(self, *args, **kwargs):
                return await interaction.followup.send(*args, **kwargs)
        return Ctx()

    @discord.app_commands.command(name="play", description="Play a song in your voice channel")
    @discord.app_commands.describe(song="Song name or YouTube URL")
    async def slash_play(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer()
        if not interaction.guild:
            return await interaction.followup.send("❌ Use this in a server.")
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send("🎙️ Join a voice channel first.")
        channel = interaction.user.voice.channel
        state = self.state(interaction.guild.id)
        state.text_channel = interaction.channel
        try:
            vc = interaction.guild.voice_client
            if not vc:
                vc = await channel.connect(self_deaf=True)
            elif vc.channel.id != channel.id and not vc.is_playing():
                await vc.move_to(channel)
            state.voice = vc
            track = await self.extract(song)
            track.requester = interaction.user.display_name
            if vc.is_playing() or vc.is_paused():
                state.queue.append(track)
                await interaction.followup.send(f"➕ Added to queue: **{track.title}**")
            else:
                state.queue.insert(0, track)
                await interaction.followup.send(f"🎵 Loading **{track.title}**…")
                await self.play_next(interaction.guild.id)
        except Exception as e:
            await interaction.followup.send(f"❌ Music error: `{str(e)[:700]}`")

    @discord.app_commands.command(name="pause", description="Pause Rani music")
    async def slash_pause(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc and vc.is_playing():
            vc.pause()
            return await interaction.followup.send("⏸️ Paused.")
        await interaction.followup.send("❌ Nothing is playing.")

    @discord.app_commands.command(name="resume", description="Resume Rani music")
    async def slash_resume(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc and vc.is_paused():
            vc.resume()
            return await interaction.followup.send("▶️ Resumed.")
        await interaction.followup.send("❌ Nothing is paused.")

    @discord.app_commands.command(name="skip", description="Skip the current song")
    async def slash_skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            return await interaction.followup.send("⏭️ Skipping.")
        await interaction.followup.send("❌ Nothing is playing.")

    @discord.app_commands.command(name="queue", description="Show the music queue")
    async def slash_queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.send_queue(interaction.followup, self.state(interaction.guild.id))

    @commands.command(name="musichelp", aliases=["mhelp"])
    async def music_help(self, ctx):
        e = discord.Embed(
            title="🔴 RANI MUSIC • CONTROL CENTER",
            description="**High-quality YouTube music • clean red UI • Made by Tyson**",
            color=RED,
        )
        e.add_field(
            name="🎵 Playback",
            value=f"`{PREFIX}play <song>`\n`{PREFIX}pause` • `{PREFIX}resume` • `{PREFIX}skip`\n`{PREFIX}stop` • `{PREFIX}nowplaying`",
            inline=False,
        )
        e.add_field(
            name="📜 Queue",
            value=f"`{PREFIX}queue` • `{PREFIX}shuffle` • `{PREFIX}remove <number>`",
            inline=False,
        )
        e.add_field(
            name="🔁 Controls",
            value=f"`{PREFIX}loop off/track/queue` • `{PREFIX}volume 1-200`\n`{PREFIX}247 on/off`",
            inline=False,
        )
        e.add_field(
            name="🎧 Voice",
            value=f"`{PREFIX}joinmusic` • `{PREFIX}leavemusic`\nYou can type a song name — Rani searches YouTube automatically.",
            inline=False,
        )
        e.set_footer(text="Rani Music • Made by Tyson")
        await ctx.reply(embed=e, view=MusicButtons(self, ctx.guild.id), mention_author=False)


async def setup(bot):
    await bot.add_cog(Music(bot))
