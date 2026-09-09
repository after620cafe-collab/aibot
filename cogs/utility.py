import discord
from discord.ext import commands
from config import PREFIX

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["commands"])
    async def help(self, ctx):
        e = discord.Embed(title="🤖 Aqua AI — Commands", description=f"Prefix: `{PREFIX}`", color=discord.Color.blurple())
        e.add_field(name="🧠 AI", value="`-ai`, `-translate`, `-rewrite`, `-summarize`, `-reset`, `-roast`, `-rizz`", inline=False)
        e.add_field(name="😂 Fun", value="`-joke`, `-8ball`, `-coinflip`, `-dice`, `-rps`, `-ship`, `-truth`, `-dare`", inline=False)
        e.add_field(name="🛡️ Mod", value="`-clear`, `-ban`, `-kick`, `-timeout`, `-warn`, `-warnings`, `-lock`, `-unlock`", inline=False)
        e.add_field(name="🖼️ Image", value="`-imagine <prompt>` — requires an image-capable Gemini model/access", inline=False)
        e.add_field(name="🎙️ Voice", value="`-joinvc`, `-leavevc` — voice foundation; STT/TTS support depends on Discord voice receive and free service limits.", inline=False)
        await ctx.reply(embed=e)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.reply(f"🏓 Pong! `{round(self.bot.latency*1000)}ms`")

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        await ctx.reply(member.display_avatar.url)

    @commands.command(name="serverinfo")
    async def serverinfo(self, ctx):
        g = ctx.guild
        e = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blurple())
        e.add_field(name="Members", value=g.member_count)
        e.add_field(name="Channels", value=len(g.channels))
        e.add_field(name="Roles", value=len(g.roles))
        await ctx.reply(embed=e)

async def setup(bot):
    await bot.add_cog(Utility(bot))
