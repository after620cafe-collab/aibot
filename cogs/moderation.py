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
        msg = await ctx.send(f"🧹 Deleted **{len(deleted)-1}** messages.")
        await msg.delete(delay=3)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.reply(f"🔨 Banned **{member}** | {reason}")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.reply(f"👢 Kicked **{member}** | {reason}")

    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10, *, reason="No reason provided"):
        minutes = max(1, min(minutes, 40320))
        await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)
        await ctx.reply(f"⏳ Timed out **{member}** for {minutes} minutes.")

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        key = (ctx.guild.id, member.id)
        self.warns[key] = self.warns.get(key, 0) + 1
        await ctx.reply(f"⚠️ {member.mention} warned. Total warnings: **{self.warns[key]}**\nReason: {reason}")

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        count = self.warns.get((ctx.guild.id, member.id), 0)
        await ctx.reply(f"⚠️ {member.mention} has **{count}** warning(s).")

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply("🔒 Channel locked.")

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.reply("🔓 Channel unlocked.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
