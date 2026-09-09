import discord
from discord.ext import commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="joinvc", aliases=["join"])
    async def joinvc(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("🎙️ Pehle kisi voice channel mein join ho jao.")
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.reply(f"🎙️ Joined **{channel.name}**!")

    @commands.command(name="leavevc", aliases=["leave"])
    async def leavevc(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.reply("👋 VC se nikal gaya.")
        else:
            await ctx.reply("Main kisi VC mein nahi hoon.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
