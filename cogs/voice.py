import os, tempfile, discord
from discord.ext import commands
from services.tts import synthesize_safe

class Voice(commands.Cog):
    def __init__(self, bot): self.bot=bot

    def vc(self, ctx):
        return ctx.guild.voice_client if ctx.guild else None

    @commands.command(name="joinvc", aliases=["join","voicemode"])
    async def joinvc(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("🎙️ Join a voice channel first.")
        channel=ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.reply(f"🎙️ Joined **{channel.name}**.", mention_author=False)

    @commands.command(name="leavevc", aliases=["leave"])
    async def leavevc(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.reply("👋 Left VC.", mention_author=False)
        else: await ctx.reply("I'm not in a VC.", mention_author=False)

    @commands.command(name="t", aliases=["tts","speak"])
    async def tts(self, ctx, *, text: str):
        vc=self.vc(ctx)
        if not vc: return await ctx.reply("🎙️ Use `-joinvc` first.", mention_author=False)
        if vc.is_playing(): vc.stop()
        path=os.path.join(tempfile.gettempdir(), f"rani_tts_{ctx.author.id}.mp3")
        await synthesize_safe(text, path)
        source=discord.FFmpegPCMAudio(path)
        vc.play(source)
        await ctx.reply("🔊 Speaking in Hindi voice.", mention_author=False)

    @commands.command(name="voicekick", aliases=["vckick","vcdisconnect"])
    @commands.has_permissions(move_members=True)
    async def voicekick(self, ctx, member: discord.Member):
        if member.voice and member.voice.channel:
            await member.move_to(None, reason=f"VC kick by {ctx.author}")
            await ctx.reply(f"👢 Removed {member.mention} from VC.", mention_author=False)

    @commands.command(name="voicemute", aliases=["vcmute"])
    @commands.has_permissions(mute_members=True)
    async def voicemute(self, ctx, member: discord.Member):
        await member.edit(mute=True, reason=f"VC mute by {ctx.author}")
        await ctx.reply(f"🔇 Server-muted {member.mention}.", mention_author=False)

    @commands.command(name="voiceunmute", aliases=["vcunmute"])
    @commands.has_permissions(mute_members=True)
    async def voiceunmute(self, ctx, member: discord.Member):
        await member.edit(mute=False, reason=f"VC unmute by {ctx.author}")
        await ctx.reply(f"🔊 Unmuted {member.mention}.", mention_author=False)

    @commands.command(name="vcdeafen")
    @commands.has_permissions(deafen_members=True)
    async def vcdeafen(self, ctx, member: discord.Member):
        await member.edit(deafen=True, reason=f"VC deafen by {ctx.author}")
        await ctx.reply(f"🙉 Deafened {member.mention}.", mention_author=False)

    @commands.command(name="vcundeafen")
    @commands.has_permissions(deafen_members=True)
    async def vcundeafen(self, ctx, member: discord.Member):
        await member.edit(deafen=False, reason=f"VC undeafen by {ctx.author}")
        await ctx.reply(f"👂 Undeafened {member.mention}.", mention_author=False)

    @commands.command(name="vcmove")
    @commands.has_permissions(move_members=True)
    async def vcmove(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        await member.move_to(channel, reason=f"VC move by {ctx.author}")
        await ctx.reply(f"↔️ Moved {member.mention} to {channel.mention}.", mention_author=False)

    @commands.command(name="vcpull")
    @commands.has_permissions(move_members=True)
    async def vcpull(self, ctx, member: discord.Member):
        if not ctx.author.voice: return await ctx.reply("❌ Join a VC first.")
        await member.move_to(ctx.author.voice.channel, reason=f"VC pull by {ctx.author}")
        await ctx.reply(f"🧲 Pulled {member.mention}.", mention_author=False)

    @commands.command(name="voiceban")
    @commands.has_permissions(manage_channels=True)
    async def voiceban(self, ctx, member: discord.Member):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("❌ Join the target voice channel first.")
        ch=ctx.author.voice.channel
        await ch.set_permissions(member, connect=False, reason=f"Voice ban by {ctx.author}")
        if member.voice and member.voice.channel == ch:
            await member.move_to(None, reason="Voice ban")
        await ctx.reply(f"🚫 Voice-banned {member.mention} from **{ch.name}**.", mention_author=False)

    @commands.command(name="voiceunban")
    @commands.has_permissions(manage_channels=True)
    async def voiceunban(self, ctx, member: discord.Member):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("❌ Join the target voice channel first.")
        ch=ctx.author.voice.channel
        await ch.set_permissions(member, connect=None, reason=f"Voice unban by {ctx.author}")
        await ctx.reply(f"✅ Voice-ban removed for {member.mention}.", mention_author=False)

async def setup(bot): await bot.add_cog(Voice(bot))
