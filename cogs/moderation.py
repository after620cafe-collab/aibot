import datetime
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        amount = max(1, min(amount, 100))
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Deleted **{max(0, len(deleted)-1)}** messages.")
        await msg.delete(delay=3)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.reply(f"🔨 **Banned:** {member.mention}\n**Reason:** {reason}", mention_author=False)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.reply(f"👢 **Kicked:** {member.mention}\n**Reason:** {reason}", mention_author=False)

    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10, *, reason="No reason provided"):
        minutes = max(1, min(minutes, 40320))
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        await ctx.reply(f"⏳ **Timed out:** {member.mention}\n**Duration:** {minutes} minutes", mention_author=False)

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        key = (ctx.guild.id, member.id)
        self.warns[key] = self.warns.get(key, 0) + 1
        await ctx.reply(f"⚠️ {member.mention} warned. Total: **{self.warns[key]}**\nReason: {reason}", mention_author=False)

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        count = self.warns.get((ctx.guild.id, member.id), 0)
        await ctx.reply(f"⚠️ {member.mention} has **{count}** warning(s).", mention_author=False)

    @commands.command(name="clearwarns")
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        self.warns.pop((ctx.guild.id, member.id), None)
        await ctx.reply(f"🧹 Cleared warnings for {member.mention}.", mention_author=False)

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply("🔒 **Channel locked.**", mention_author=False)

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply("🔓 **Channel unlocked.**", mention_author=False)

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        seconds = max(0, min(seconds, 21600))
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.reply(f"🐢 Slowmode set to **{seconds}s**.", mention_author=False)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
