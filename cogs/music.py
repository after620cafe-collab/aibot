import asyncio
import random
from dataclasses import dataclass, field
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

from config import PREFIX

RED = discord.Color.from_rgb(220, 35, 55)

YTDL_OPTIONS = {
    "format": "bestaudio[ext=webm]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch1",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "ignoreerrors": False,
    "remote_components": "ejs:github",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -reconnect_at_eof 1 -nostdin",
    "options": "-vn -ac 2 -ar 48000 -b:a 192k -bufsize 512k",
}

YTDL = yt_dlp.YoutubeDL(YTDL_OPTIONS)

@dataclass
class Track:
    title: str
    stream_url: str
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
    loop: str = "off"
    stay_24_7: bool = False
    text_channel: Optional[discord.TextChannel] = None
    play_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def fmt_time(seconds: int) -> str:
    if not seconds:
        return "LIVE"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

class MusicButtons(discord.ui.View):
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=600)
        self.cog = cog
        self.guild_id = guild_id

    async def do(self, interaction: discord.Interaction, action: str):
        await interaction.response.defer()
        state = self.cog.state(self.guild_id)
        vc = state.voice or interaction.guild.voice_client
        if not vc:
            return await interaction.followup.send("❌ Rani is not in voice.", ephemeral=True)
        state.voice = vc
        if action == "pause" and vc.is_playing():
            vc.pause(); return await interaction.followup.send("⏸️ Paused.", ephemeral=True)
        if action == "resume" and vc.is_paused():
            vc.resume(); return await interaction.followup.send("▶️ Resumed.", ephemeral=True)
        if action == "skip" and (vc.is_playing() or vc.is_paused()):
            vc.stop(); return await interaction.followup.send("⏭️ Skipping.", ephemeral=True)
        if action == "stop":
            state.queue.clear(); state.current = None; state.loop = "off"
            if vc.is_playing() or vc.is_paused(): vc.stop()
            return await interaction.followup.send("⏹️ Stopped and queue cleared.", ephemeral=True)
        if action == "queue":
            return await self.cog.send_queue(interaction.followup, state)
        await interaction.followup.send("ℹ️ Nothing to do right now.", ephemeral=True)

    @discord.ui.button(label="Pause", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button): await self.do(interaction, "pause")
    @discord.ui.button(label="Resume", emoji="▶️", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button): await self.do(interaction, "resume")
    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button): await self.do(interaction, "skip")
    @discord.ui.button(label="Queue", emoji="📜", style=discord.ButtonStyle.secondary)
    async def queue(self, interaction, button): await self.do(interaction, "queue")
    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop(self, interaction, button): await self.do(interaction, "stop")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states: dict[int, GuildMusic] = {}
        self.tasks: set[asyncio.Future] = set()

    def state(self, guild_id: int) -> GuildMusic:
        return self.states.setdefault(guild_id, GuildMusic())

    async def extract(self, query: str) -> Track:
        def run():
            target = query if query.startswith(("http://", "https://")) else f"ytsearch1:{query}"
            data = YTDL.extract_info(target, download=False)
            if not data:
                raise RuntimeError("No YouTube result found.")
            if "entries" in data:
                data = next((x for x in data["entries"] if x), None)
            if not data or not data.get("url"):
                raise RuntimeError("YouTube returned no playable audio stream.")
            return Track(
                title=data.get("title") or "Unknown track",
                stream_url=data["url"],
                webpage=data.get("webpage_url") or data.get("original_url") or query,
                duration=int(data.get("duration") or 0),
                thumbnail=data.get("thumbnail") or "",
            )
        return await asyncio.wait_for(asyncio.to_thread(run), timeout=45)

    async def ensure_voice(self, ctx) -> Optional[discord.VoiceClient]:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("🎙️ Pehle voice channel join karo.", mention_author=False)
            return None
        channel = ctx.author.voice.channel
        state = self.state(ctx.guild.id)
        vc = ctx.guild.voice_client
        if vc:
            state.voice = vc
            if vc.channel.id != channel.id and not vc.is_playing():
                await vc.move_to(channel)
            return vc
        try:
            vc = await channel.connect(self_deaf=True)
            state.voice = vc
            return vc
        except Exception as e:
            await ctx.reply(f"❌ Voice join failed: `{e}`", mention_author=False)
            return None

    def player_embed(self, track: Track, state: GuildMusic):
        e = discord.Embed(title="🔴 RANI MUSIC • NOW PLAYING", description=f"**[{track.title}]({track.webpage})**", color=RED)
        e.add_field(name="⏱️ Duration", value=fmt_time(track.duration), inline=True)
        e.add_field(name="🔊 Volume", value=f"{round(state.volume*100)}%", inline=True)
        e.add_field(name="🔁 Loop", value=state.loop.upper(), inline=True)
        if track.requester: e.add_field(name="👤 Requested by", value=track.requester, inline=True)
        if state.stay_24_7: e.add_field(name="♾️ 24/7", value="ON", inline=True)
        if track.thumbnail: e.set_thumbnail(url=track.thumbnail)
        e.set_footer(text="Rani Music • Made by Tyson")
        return e

    async def play_next(self, guild_id: int):
        state = self.state(guild_id)
        async with state.play_lock:
            vc = state.voice
            if not vc or not vc.is_connected(): return
            if state.loop == "track" and state.current:
                track = state.current
            elif state.queue:
                track = state.queue.pop(0)
            elif state.loop == "queue" and state.current:
                track = state.current
            elif state.stay_24_7 and state.current:
                track = state.current
            else:
                state.current = None; return

            # Refresh the stream URL immediately before playback; YouTube URLs expire.
            try:
                fresh = await self.extract(track.webpage)
                track.stream_url = fresh.stream_url
                track.title = fresh.title or track.title
                track.duration = fresh.duration or track.duration
                track.thumbnail = fresh.thumbnail or track.thumbnail
            except Exception as e:
                if state.text_channel:
                    await state.text_channel.send(f"⚠️ Couldn't refresh **{track.title}**: `{str(e)[:500]}`")
                if state.queue:
                    return await self.play_next(guild_id)
                return

            state.current = track
            def after(error):
                if error: logging_msg = f"[Rani Music] {guild_id}: {error}"; print(logging_msg)
                fut = asyncio.run_coroutine_threadsafe(self.play_next(guild_id), self.bot.loop)
                self.tasks.add(fut); fut.add_done_callback(self.tasks.discard)

            try:
                source = discord.FFmpegOpusAudio(track.stream_url, before_options=FFMPEG_OPTIONS["before_options"], options=FFMPEG_OPTIONS["options"])
                source = discord.PCMVolumeTransformer(source, volume=state.volume)
                vc.play(source, after=after)
                if state.text_channel:
                    await state.text_channel.send(embed=self.player_embed(track, state), view=MusicButtons(self, guild_id))
            except Exception as e:
                if state.text_channel:
                    await state.text_channel.send(f"⚠️ **Playback failed:** `{str(e)[:600]}`")
                if state.queue:
                    return await self.play_next(guild_id)

    async def send_queue(self, destination, state):
        e = discord.Embed(title="🔴 RANI MUSIC • QUEUE", color=RED)
        e.add_field(name="🎵 Now", value=f"**{state.current.title}**" if state.current else "Nothing playing", inline=False)
        if state.queue:
            e.add_field(name="📜 Up Next", value="\n".join(f"`{i}.` {t.title}" for i,t in enumerate(state.queue[:15],1)), inline=False)
        else: e.add_field(name="📜 Up Next", value="Queue empty.", inline=False)
        e.set_footer(text=f"Loop: {state.loop.upper()} • 24/7: {'ON' if state.stay_24_7 else 'OFF'} • Made by Tyson")
        return await destination.send(embed=e)

    async def do_play(self, ctx, query: str):
        vc = await self.ensure_voice(ctx)
        if not vc: return
        state = self.state(ctx.guild.id); state.text_channel = ctx.channel
        msg = await ctx.reply("🔎 **Rani is searching YouTube...**", mention_author=False)
        try:
            track = await self.extract(query); track.requester = ctx.author.display_name
            if vc.is_playing() or vc.is_paused():
                state.queue.append(track); return await msg.edit(content=f"➕ **Added:** `{track.title}`")
            state.queue.insert(0, track)
            await msg.edit(content=f"🎵 **Loading:** `{track.title}`")
            await self.play_next(ctx.guild.id)
        except asyncio.TimeoutError:
            await msg.edit(content="❌ YouTube timed out. Try again.")
        except Exception as e:
            await msg.edit(content=f"❌ **Music error:** `{str(e)[:900]}`")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str): await self.do_play(ctx, query)

    @app_commands.command(name="play", description="Play a song from YouTube")
    @app_commands.describe(query="Song name or YouTube URL")
    async def slash_play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        class Ctx:
            guild=interaction.guild; author=interaction.user; channel=interaction.channel
            async def reply(self, content=None, **kwargs): return await interaction.followup.send(content, **kwargs)
        await self.do_play(Ctx(), query)

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc=ctx.guild.voice_client
        if vc and vc.is_playing(): vc.pause(); await ctx.reply("⏸️ **Paused.**", mention_author=False)
        else: await ctx.reply("❌ Nothing is playing.", mention_author=False)

    @app_commands.command(name="pause", description="Pause music")
    async def slash_pause(self, interaction):
        vc=interaction.guild.voice_client if interaction.guild else None
        if vc and vc.is_playing(): vc.pause(); await interaction.response.send_message("⏸️ **Paused.**")
        else: await interaction.response.send_message("❌ Nothing is playing.")

    @commands.command(name="resume", aliases=["unpause"])
    async def resume(self, ctx):
        vc=ctx.guild.voice_client
        if vc and vc.is_paused(): vc.resume(); await ctx.reply("▶️ **Resumed.**", mention_author=False)
        else: await ctx.reply("❌ Nothing is paused.", mention_author=False)

    @app_commands.command(name="resume", description="Resume music")
    async def slash_resume(self, interaction):
        vc=interaction.guild.voice_client if interaction.guild else None
        if vc and vc.is_paused(): vc.resume(); await interaction.response.send_message("▶️ **Resumed.**")
        else: await interaction.response.send_message("❌ Nothing is paused.")

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        vc=ctx.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()): vc.stop(); await ctx.reply("⏭️ **Skipped.**", mention_author=False)
        else: await ctx.reply("❌ Nothing is playing.", mention_author=False)

    @app_commands.command(name="skip", description="Skip current song")
    async def slash_skip(self, interaction):
        vc=interaction.guild.voice_client if interaction.guild else None
        if vc and (vc.is_playing() or vc.is_paused()): vc.stop(); await interaction.response.send_message("⏭️ **Skipped.**")
        else: await interaction.response.send_message("❌ Nothing is playing.")

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx): await self.send_queue(ctx, self.state(ctx.guild.id))

    @app_commands.command(name="queue", description="Show music queue")
    async def slash_queue(self, interaction): await self.send_queue(interaction.response, self.state(interaction.guild.id)) if False else await interaction.response.send_message(embed=discord.Embed(title="🔴 RANI MUSIC • QUEUE", description="Use `-queue` for the full queue.", color=RED))

    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        state=self.state(ctx.guild.id)
        if not state.current: return await ctx.reply("❌ Nothing is playing.", mention_author=False)
        await ctx.reply(embed=self.player_embed(state.current,state),view=MusicButtons(self,ctx.guild.id),mention_author=False)

    @app_commands.command(name="nowplaying", description="Show current song")
    async def slash_nowplaying(self, interaction):
        state=self.state(interaction.guild.id)
        if not state.current: return await interaction.response.send_message("❌ Nothing is playing.")
        await interaction.response.send_message(embed=self.player_embed(state.current,state),view=MusicButtons(self,interaction.guild.id))

    @commands.command(name="stop", aliases=["disconnect"])
    async def stop(self, ctx):
        state=self.state(ctx.guild.id); state.queue.clear(); state.current=None; state.loop="off"
        if ctx.guild.voice_client: await ctx.guild.voice_client.disconnect(force=True)
        state.voice=None; await ctx.reply("⏹️ **Music stopped.**",mention_author=False)

    @commands.command(name="joinmusic", aliases=["joinvc","musicjoin"])
    async def joinmusic(self, ctx):
        vc=await self.ensure_voice(ctx)
        if vc: self.state(ctx.guild.id).text_channel=ctx.channel; await ctx.reply(f"🎧 **Rani joined:** `{vc.channel.name}`",mention_author=False)

    @commands.command(name="leavemusic", aliases=["leavevc","musicleave"])
    async def leavemusic(self, ctx):
        state=self.state(ctx.guild.id); state.stay_24_7=False; state.queue.clear(); state.current=None
        if ctx.guild.voice_client: await ctx.guild.voice_client.disconnect(force=True)
        state.voice=None; await ctx.reply("👋 **Rani left voice.**",mention_author=False)

    @commands.command(name="volume", aliases=["vol"])
    @commands.has_permissions(manage_guild=True)
    async def volume(self, ctx, level: int):
        if not 1<=level<=200: return await ctx.reply("🔊 Use 1-200.",mention_author=False)
        state=self.state(ctx.guild.id); state.volume=level/100
        vc=ctx.guild.voice_client
        if vc and isinstance(getattr(vc,"source",None),discord.PCMVolumeTransformer): vc.source.volume=state.volume
        await ctx.reply(f"🔊 Volume **{level}%**",mention_author=False)

    @commands.command(name="loop")
    async def loop(self, ctx, mode: str="track"):
        mode=mode.lower()
        if mode not in ("off","track","queue"): return await ctx.reply("🔁 `-loop off/track/queue`",mention_author=False)
        self.state(ctx.guild.id).loop=mode; await ctx.reply(f"🔁 Loop **{mode.upper()}**",mention_author=False)

    @commands.command(name="247", aliases=["24/7","stay"])
    async def always_on(self, ctx, mode: str="on"):
        mode=mode.lower()
        if mode not in ("on","off"): return await ctx.reply("♾️ `-247 on/off`",mention_author=False)
        state=self.state(ctx.guild.id); state.stay_24_7=mode=="on"
        if state.stay_24_7: state.loop="track"
        await ctx.reply(f"♾️ **24/7 {'ON' if state.stay_24_7 else 'OFF'}**",mention_author=False)

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        state=self.state(ctx.guild.id)
        if len(state.queue)<2: return await ctx.reply("🔀 Need 2+ queued songs.",mention_author=False)
        random.shuffle(state.queue); await ctx.reply("🔀 **Queue shuffled.**",mention_author=False)

    @commands.command(name="remove")
    async def remove(self, ctx, position: int):
        state=self.state(ctx.guild.id)
        if not 1<=position<=len(state.queue): return await ctx.reply("❌ Invalid position.",mention_author=False)
        t=state.queue.pop(position-1); await ctx.reply(f"🗑️ Removed **{t.title}**",mention_author=False)

    @commands.command(name="musichelp", aliases=["mhelp"])
    async def musichelp(self, ctx):
        e=discord.Embed(title="🔴 RANI MUSIC • CONTROL CENTER",description="**Premium red music UI • Made by Tyson**",color=RED)
        e.add_field(name="🎵 Play",value=f"`{PREFIX}play <song>` / `/play`",inline=False)
        e.add_field(name="⏯️ Controls",value=f"`{PREFIX}pause` `resume` `skip` `stop` `nowplaying`",inline=False)
        e.add_field(name="📜 Queue",value=f"`{PREFIX}queue` `shuffle` `remove <number>`",inline=False)
        e.add_field(name="♾️ Pro",value=f"`{PREFIX}loop off/track/queue` `volume 1-200` `247 on/off`",inline=False)
        e.set_footer(text="Rani AI • Created by Tyson")
        await ctx.reply(embed=e,view=MusicButtons(self,ctx.guild.id),mention_author=False)

async def setup(bot):
    await bot.add_cog(Music(bot))
