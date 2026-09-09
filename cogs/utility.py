import discord
from discord.ext import commands
from config import PREFIX

BRAND = "Aqua AI"
MADE_BY = "Tyson"

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    def embed(self, title, description, fields):
        e = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(88, 101, 242))
        for name, value in fields:
            e.add_field(name=name, value=value, inline=False)
        e.set_footer(text="Aqua AI • Made by Tyson")
        return e

    async def update(self, interaction, title, description, fields):
        await interaction.response.edit_message(embed=self.embed(title, description, fields), view=self)

    @discord.ui.button(label="AI", emoji="🧠", style=discord.ButtonStyle.primary)
    async def ai(self, interaction, button):
        await self.update(interaction, "🧠 AI Commands", "Smart tools powered by Gemini.", [
            ("Chat", f"`{PREFIX}ai <message>` • `{PREFIX}ask <message>`"),
            ("Creative", f"`{PREFIX}roast @user` • `{PREFIX}rizz <situation>`"),
            ("Text Tools", f"`{PREFIX}translate <language> <text>`\n`{PREFIX}rewrite <style> <text>`\n`{PREFIX}summarize <text>`\n`{PREFIX}explain <topic>`\n`{PREFIX}code <request>`"),
            ("Memory", f"`{PREFIX}reset` — clear your AI memory")
        ])

    @discord.ui.button(label="Fun", emoji="🎮", style=discord.ButtonStyle.secondary)
    async def fun(self, interaction, button):
        await self.update(interaction, "🎮 Fun & Games", "Quick commands for the server.", [
            ("Games", f"`{PREFIX}8ball <question>` • `{PREFIX}rps <rock/paper/scissors>` • `{PREFIX}dice [sides]` • `{PREFIX}coinflip`"),
            ("Social", f"`{PREFIX}ship @a @b` • `{PREFIX}rate <thing>` • `{PREFIX}choose <a> | <b> | ...`"),
            ("AI Fun", f"`{PREFIX}joke` • `{PREFIX}truth` • `{PREFIX}dare` • `{PREFIX}compliment @user` • `{PREFIX}pickup`"),
        ])

    @discord.ui.button(label="Mod", emoji="🛡️", style=discord.ButtonStyle.danger)
    async def mod(self, interaction, button):
        await self.update(interaction, "🛡️ Moderation", "Commands require the matching Discord permissions.", [
            ("Moderate", f"`{PREFIX}clear [amount]` • `{PREFIX}ban @user [reason]` • `{PREFIX}kick @user [reason]`\n`{PREFIX}timeout @user [minutes]` • `{PREFIX}warn @user [reason]`"),
            ("Warnings", f"`{PREFIX}warnings @user` • `{PREFIX}clearwarns @user`"),
            ("Channel", f"`{PREFIX}lock` • `{PREFIX}unlock` • `{PREFIX}slowmode <seconds>`")
        ])

    @discord.ui.button(label="Tools", emoji="🔧", style=discord.ButtonStyle.secondary)
    async def tools(self, interaction, button):
        await self.update(interaction, "🔧 Server Tools", "Useful everyday commands.", [
            ("Info", f"`{PREFIX}ping` • `{PREFIX}serverinfo` • `{PREFIX}userinfo @user` • `{PREFIX}avatar @user`"),
            ("Utility", f"`{PREFIX}poll <question>` • `{PREFIX}say <text>` (Manage Messages required)"),
            ("Voice", f"`{PREFIX}joinvc` • `{PREFIX}leavevc`")
        ])

    @discord.ui.button(label="Image", emoji="🎨", style=discord.ButtonStyle.success)
    async def image(self, interaction, button):
        await self.update(interaction, "🎨 AI Image", "Gemini image generation.", [
            ("Generate", f"`{PREFIX}imagine <prompt>`"),
            ("Example", f"`{PREFIX}imagine a cinematic neon city at night, 16:9`"),
            ("Note", "Image generation needs a Gemini key with access to the configured image model.")
        ])

    @discord.ui.button(label="Home", emoji="🏠", style=discord.ButtonStyle.success, row=1)
    async def home(self, interaction, button):
        await self.update(interaction, "🤖 Aqua AI", f"**Your all-in-one Discord assistant**\nPrefix: `{PREFIX}`\n\nChoose a category below.", [
            ("✨ Highlights", "AI chat • image generation • moderation • games • utilities"),
            ("👨‍💻 Developer", "Made by **Tyson**"),
        ])

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["commands", "menu"])
    async def help(self, ctx):
        e = discord.Embed(
            title="🤖 Aqua AI",
            description=f"**Your all-in-one Discord assistant**\n\nPrefix: `{PREFIX}`\nUse the buttons below to browse commands.",
            color=discord.Color.from_rgb(88, 101, 242),
        )
        e.add_field(name="✨ Features", value="🧠 AI  •  🎨 Images  •  🛡️ Moderation  •  🎮 Fun  •  🔧 Tools", inline=False)
        e.add_field(name="👨‍💻 Developer", value="**Made by Tyson**", inline=False)
        e.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user else discord.Embed.Empty)
        e.set_footer(text="Aqua AI • Made by Tyson")
        await ctx.reply(embed=e, view=HelpView(self.bot), mention_author=False)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.reply(f"🏓 **Pong!** `{round(self.bot.latency * 1000)}ms`", mention_author=False)

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        e = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=discord.Color.blurple())
        e.set_image(url=member.display_avatar.url)
        e.set_footer(text="Aqua AI • Made by Tyson")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(name="serverinfo", aliases=["server"])
    async def serverinfo(self, ctx):
        g = ctx.guild
        e = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blurple())
        e.add_field(name="Members", value=str(g.member_count))
        e.add_field(name="Channels", value=str(len(g.channels)))
        e.add_field(name="Roles", value=str(len(g.roles)))
        e.add_field(name="Owner", value=g.owner.mention if g.owner else "Unknown")
        e.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        e.set_footer(text="Aqua AI • Made by Tyson")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(name="userinfo", aliases=["user"])
    async def userinfo(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        e = discord.Embed(title=f"👤 {member.display_name}", color=discord.Color.blurple())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="Username", value=str(member), inline=False)
        e.add_field(name="ID", value=str(member.id), inline=True)
        e.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "Unknown", inline=True)
        e.set_footer(text="Aqua AI • Made by Tyson")
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(name="poll")
    async def poll(self, ctx, *, question: str):
        e = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blurple())
        e.set_footer(text="Aqua AI • Made by Tyson")
        msg = await ctx.send(embed=e)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text)

async def setup(bot):
    await bot.add_cog(Utility(bot))
