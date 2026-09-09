import discord
from discord.ext import commands
from config import PREFIX

RED=discord.Color.from_rgb(220, 35, 55)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot=bot

    async def update(self, interaction, title, desc, fields):
        e=discord.Embed(title=title, description=desc, color=RED)
        for name,value in fields: e.add_field(name=name,value=value,inline=False)
        e.set_footer(text="Made by Tyson • Rani AI")
        await interaction.response.edit_message(embed=e, view=self)

    @discord.ui.select(
        placeholder="Choose a command category...",
        options=[
            discord.SelectOption(label="Home",emoji="🏠",description="Bot overview",value="home"),
            discord.SelectOption(label="AI",emoji="🧠",description="AI and translation",value="ai"),
            discord.SelectOption(label="Moderation",emoji="🛡️",description="Server moderation",value="mod"),
            discord.SelectOption(label="Voice",emoji="🎙️",description="VC + Hindi TTS",value="voice"),
            discord.SelectOption(label="Music",emoji="🎵",description="High-quality music player",value="music"),
            discord.SelectOption(label="Automation",emoji="⚙️",description="Autoresponder and reactions",value="auto"),
            discord.SelectOption(label="Roles",emoji="🎭",description="Custom role tools",value="roles"),
            discord.SelectOption(label="Fun / Pranks",emoji="🎁",description="Games and Nitro prank",value="fun"),
            discord.SelectOption(label="Utility",emoji="🔧",description="Server utilities",value="utility"),
        ])
    async def select(self, interaction, select):
        v=select.values[0]
        if v=="home":
            await self.update(interaction,"🔴 Rani AI • Command Center","Professional all-in-one Discord bot.",[
                ("⚡ Prefix",f"`{PREFIX}`"),("✨ Features","AI • Moderation • Voice • TTS • Automation • Roles • Fun"),("👨‍💻 Developer","**Made by Tyson**")])
        elif v=="ai":
            await self.update(interaction,"🧠 AI & Text", "Free-tier Groq powered AI.",[
                ("Chat",f"`{PREFIX}ai <message>` • `/ai <message>`"),
                ("Text",f"`{PREFIX}translate <language> <text>`\n`{PREFIX}rewrite <style> <text>`\n`{PREFIX}summarize <text>`\n`{PREFIX}explain <topic>`\n`{PREFIX}code <request>`"),
                ("Memory",f"`{PREFIX}reset`")])
        elif v=="mod":
            await self.update(interaction,"🛡️ Moderation","Powerful moderation tools.",[
                ("Members",f"`{PREFIX}ban` • `{PREFIX}unban` • `{PREFIX}unbanall confirm` • `{PREFIX}kick`\n`{PREFIX}mute` • `{PREFIX}unmute` • `{PREFIX}unmuteall confirm` • `{PREFIX}warn`"),
                ("Channel",f"`{PREFIX}clear` • `{PREFIX}lock` • `{PREFIX}unlock` • `{PREFIX}hide` • `{PREFIX}unhide` • `{PREFIX}slowmode` • `{PREFIX}clone` • `{PREFIX}snipe`"),
                ("Warnings",f"`{PREFIX}warnings` • `{PREFIX}clearwarns`")])
        elif v=="voice":
            await self.update(interaction,"🎙️ Voice Center","VC controls + Hindi female TTS.",[
                ("TTS",f"`{PREFIX}t <text>` — Hindi voice\n`{PREFIX}joinvc` • `{PREFIX}leavevc`"),
                ("VC Mod",f"`{PREFIX}voicekick` • `{PREFIX}voicemute` • `{PREFIX}voiceunmute`\n`{PREFIX}vcdeafen` • `{PREFIX}vcundeafen` • `{PREFIX}vcmove` • `{PREFIX}vcpull`\n`{PREFIX}voiceban` • `{PREFIX}voiceunban`")])
        elif v=="music":
            await self.update(interaction,"🎵 Rani Music • Premium Player","High-quality music controls with a clean red UI.",[
                ("🎧 Play",f"`{PREFIX}play <song>` • `{PREFIX}joinmusic` • `{PREFIX}leavemusic`"),
                ("⏯️ Controls",f"`{PREFIX}pause` • `{PREFIX}resume` • `{PREFIX}skip` • `{PREFIX}stop` • `{PREFIX}nowplaying`"),
                ("📜 Queue",f"`{PREFIX}queue` • `{PREFIX}shuffle` • `{PREFIX}remove <number>`"),
                ("🔁 Pro",f"`{PREFIX}loop off/track/queue` • `{PREFIX}volume 1-200` • `{PREFIX}247 on/off`"),
                ("✨ How it works","Type any song name and Rani searches YouTube automatically. 24/7 mode keeps the last track playing when the queue is empty.")])
        elif v=="auto":
            await self.update(interaction,"⚙️ Automation","Automatic server responses and reactions.",[
                ("Auto Reply",f"`{PREFIX}autoresponder add hello Hi!` • `{PREFIX}autoresponder list` • `{PREFIX}autoresponder remove hello`"),
                ("Mention Reaction",f"`{PREFIX}tagreaction ❤️`"),
                ("Automation",f"`{PREFIX}automation on` / `{PREFIX}automation off`")])
        elif v=="roles":
            await self.update(interaction,"🎭 Roles","Custom role management.",[
                ("Roles",f"`{PREFIX}createrole <name>` • `{PREFIX}deleterole @role`\n`{PREFIX}giverole @user @role` • `{PREFIX}removerole @user @role`\n`{PREFIX}reactionrole @role` • `{PREFIX}rolecolor @role #ff0000`")])
        elif v=="fun":
            await self.update(interaction,"🎁 Fun & Pranks","Games plus a safe Nitro-style prank.",[
                ("Games",f"`{PREFIX}8ball` • `{PREFIX}coinflip` • `{PREFIX}dice` • `{PREFIX}rps` • `{PREFIX}joke` • `{PREFIX}truth` • `{PREFIX}dare` • `{PREFIX}choose` • `{PREFIX}rate`"),
                ("Prank",f"`{PREFIX}nitro` — fake claim animation, no links/login/payment.")])
        elif v=="utility":
            await self.update(interaction,"🔧 Utility","Everyday server tools.",[
                ("Info",f"`{PREFIX}ping` • `{PREFIX}serverinfo` • `{PREFIX}userinfo` • `{PREFIX}avatar`"),
                ("Community",f"`{PREFIX}poll <question>` • `{PREFIX}say <text>`")])

class Utility(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @commands.command(name="help", aliases=["commands","menu"])
    async def help(self, ctx):
        e=discord.Embed(title="🔴 Rani AI • Help Center",description="**Professional Discord command center**\nSelect a category below.",color=RED)
        e.add_field(name="⚡ Prefix",value=f"`{PREFIX}`",inline=True)
        e.add_field(name="👨‍💻 Developer",value="**Made by Tyson**",inline=True)
        e.add_field(name="✨ Modules",value="🧠 AI  •  🎵 Music  •  🛡️ Mod  •  🎙️ Voice  •  ⚙️ Automation  •  🎭 Roles  •  🎁 Fun",inline=False)
        e.set_footer(text="Rani AI • Made by Tyson")
        await ctx.reply(embed=e,view=HelpView(self.bot),mention_author=False)

    @commands.command(name="ping")
    async def ping(self,ctx): await ctx.reply(f"🏓 **Pong** `{round(self.bot.latency*1000)}ms`",mention_author=False)

    @commands.command(name="avatar",aliases=["av"])
    async def avatar(self,ctx,member:discord.Member|None=None):
        member=member or ctx.author
        e=discord.Embed(title=f"🖼️ {member.display_name}",color=RED); e.set_image(url=member.display_avatar.url); await ctx.reply(embed=e,mention_author=False)

    @commands.command(name="serverinfo",aliases=["server"])
    async def serverinfo(self,ctx):
        g=ctx.guild; e=discord.Embed(title=f"📊 {g.name}",color=RED)
        e.add_field(name="Members",value=str(g.member_count)); e.add_field(name="Channels",value=str(len(g.channels))); e.add_field(name="Roles",value=str(len(g.roles)))
        await ctx.reply(embed=e,mention_author=False)

    @commands.command(name="userinfo",aliases=["user"])
    async def userinfo(self,ctx,member:discord.Member|None=None):
        m=member or ctx.author; e=discord.Embed(title=f"👤 {m.display_name}",color=RED)
        e.set_thumbnail(url=m.display_avatar.url); e.add_field(name="User",value=str(m),inline=False); e.add_field(name="ID",value=str(m.id))
        await ctx.reply(embed=e,mention_author=False)

    @commands.command(name="poll")
    async def poll(self,ctx,*,question:str):
        e=discord.Embed(title="📊 Poll",description=question,color=RED); msg=await ctx.send(embed=e); await msg.add_reaction("👍"); await msg.add_reaction("👎")

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self,ctx,*,text:str):
        await ctx.message.delete(); await ctx.send(text)

async def setup(bot): await bot.add_cog(Utility(bot))
