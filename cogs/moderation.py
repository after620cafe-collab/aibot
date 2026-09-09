import datetime
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}

    async def target_guard(self, ctx, member):
        if member == ctx.author:
            await ctx.reply("❌ You can't use this on yourself.", mention_author=False)
            return False
        if member == ctx.guild.owner:
            await ctx.reply("❌ You can't moderate the server owner.", mention_author=False)
            return False
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.reply("❌ That member's role is equal/higher than yours.", mention_author=False)
            return False
        return True

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        deleted = await ctx.channel.purge(limit=max(1, min(amount, 100)) + 1)
        msg = await ctx.send(f"🧹 Deleted **{max(0,len(deleted)-1)}** messages.")
        await msg.delete(delay=3)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not await self.target_guard(ctx, member): return
        await member.ban(reason=reason)
        await ctx.reply(f"🔨 Banned {member.mention}\nReason: {reason}", mention_author=False)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.reply(f"🔓 Unbanned **{user}**.", mention_author=False)

    @commands.command(name="unbanall")
    @commands.has_permissions(administrator=True)
    async def unbanall(self, ctx, confirm: str = ""):
        if confirm.lower() != "confirm":
            return await ctx.reply("⚠️ This mass action is protected. Use `-unbanall confirm`.", mention_author=False)
        bans = [entry async for entry in ctx.guild.bans(limit=None)]
        count = 0
        for entry in bans:
            try:
                await ctx.guild.unban(entry.user, reason=f"Unban all by {ctx.author}")
                count += 1
            except discord.HTTPException:
                pass
        await ctx.reply(f"🔓 Unbanned **{count}** users.", mention_author=False)

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not await self.target_guard(ctx, member): return
        await member.kick(reason=reason)
        await ctx.reply(f"👢 Kicked {member.mention}\nReason: {reason}", mention_author=False)

    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int = 10, *, reason="No reason provided"):
        if not await self.target_guard(ctx, member): return
        minutes = max(1, min(minutes, 40320))
        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        await ctx.reply(f"🔇 Muted {member.mention} for **{minutes}m**.", mention_author=False)

    @commands.command(name="unmute", aliases=["untimeout"])
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        if not await self.target_guard(ctx, member): return
        await member.timeout(None, reason=f"Unmute by {ctx.author}")
        await ctx.reply(f"🔊 Unmuted {member.mention}.", mention_author=False)

    @commands.command(name="unmuteall", aliases=["untimeoutall"])
    @commands.has_permissions(administrator=True)
    async def unmuteall(self, ctx, confirm: str = ""):
        if confirm.lower() != "confirm":
            return await ctx.reply("⚠️ Use `-unmuteall confirm` for this mass action.", mention_author=False)
        count = 0
        for m in ctx.guild.members:
            if m.is_timed_out():
                try:
                    await m.timeout(None, reason=f"Unmute all by {ctx.author}")
                    count += 1
                except discord.HTTPException: pass
        await ctx.reply(f"🔊 Cleared timeouts for **{count}** members.", mention_author=False)

    @commands.command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not await self.target_guard(ctx, member): return
        key=(ctx.guild.id, member.id)
        self.warns[key]=self.warns.get(key,0)+1
        await ctx.reply(f"⚠️ {member.mention} warned. Total: **{self.warns[key]}**\nReason: {reason}", mention_author=False)

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        await ctx.reply(f"⚠️ {member.mention} has **{self.warns.get((ctx.guild.id,member.id),0)}** warning(s).", mention_author=False)

    @commands.command(name="clearwarns")
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, member: discord.Member):
        self.warns.pop((ctx.guild.id,member.id), None)
        await ctx.reply(f"🧽 Cleared warnings for {member.mention}.", mention_author=False)

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.reply("🔒 Channel locked.", mention_author=False)

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.reply("🔓 Channel unlocked.", mention_author=False)

    @commands.command(name="hide")
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.reply("🙈 Channel hidden from @everyone.", mention_author=False)

    @commands.command(name="unhide")
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=None)
        await ctx.reply("👀 Channel visible to @everyone.", mention_author=False)

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        seconds=max(0,min(seconds,21600))
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.reply(f"🐢 Slowmode: **{seconds}s**", mention_author=False)

    @commands.command(name="clone")
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx):
        new = await ctx.channel.clone(reason=f"Clone by {ctx.author}")
        await new.edit(position=ctx.channel.position+1)
        await ctx.reply(f"📋 Cloned channel: {new.mention}", mention_author=False)

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        cog=self.bot.get_cog("Automation")
        item=cog.deleted.get(ctx.channel.id) if cog else None
        if not item: return await ctx.reply("🕵️ Nothing to snipe.", mention_author=False)
        author, content, attachments=item
        e=discord.Embed(title="🕵️ Snipe", description=content or "*No text*", color=discord.Color.red())
        e.set_author(name=str(author), icon_url=author.display_avatar.url)
        if attachments: e.add_field(name="Attachments", value="\n".join(attachments[:5]), inline=False)
        await ctx.reply(embed=e, mention_author=False)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
