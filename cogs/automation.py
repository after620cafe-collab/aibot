import json, os, discord
from discord.ext import commands

DATA="automation.json"

class Automation(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.autoreplies={}
        self.tag_reaction={}
        self.deleted={}
        self.load()

    def load(self):
        if not os.path.exists(DATA): return
        try:
            with open(DATA,"r",encoding="utf8") as f:
                d=json.load(f)
            self.autoreplies=d.get("autoreplies",{})
            self.tag_reaction=d.get("tag_reaction",{})
        except Exception: pass

    def save(self):
        try:
            with open(DATA,"w",encoding="utf8") as f:
                json.dump({"autoreplies":self.autoreplies,"tag_reaction":self.tag_reaction},f,indent=2)
        except Exception: pass

    @commands.hybrid_command(name="autoresponder", aliases=["ar"])
    @commands.has_permissions(manage_guild=True)
    async def autoresponder(self, ctx, action: str, trigger: str, *, response: str=""):
        gid=str(ctx.guild.id)
        self.autoreplies.setdefault(gid,{})
        if action.lower() in {"add","set"}:
            if not response: return await ctx.reply("Use `-autoresponder add hello Hi there!`")
            self.autoreplies[gid][trigger.lower()]=response
            self.save()
            return await ctx.reply(f"🤖 Auto-reply added for `{trigger}`.")
        if action.lower() == "remove":
            self.autoreplies[gid].pop(trigger.lower(),None); self.save()
            return await ctx.reply(f"🗑️ Auto-reply removed for `{trigger}`.")
        if action.lower() == "list":
            vals=self.autoreplies.get(gid,{})
            return await ctx.reply("📋 " + (", ".join(f"`{k}`" for k in vals) or "No auto-replies."))
        await ctx.reply("Use `add`, `remove`, or `list`.")

    @commands.hybrid_command(name="tagreaction", aliases=["tagreact"])
    @commands.has_permissions(manage_guild=True)
    async def tagreaction(self, ctx, emoji: str):
        self.tag_reaction[str(ctx.guild.id)]=emoji
        self.save()
        await ctx.reply(f"💗 I'll react with {emoji} when someone tags me.")

    @commands.hybrid_command(name="automation")
    @commands.has_permissions(manage_guild=True)
    async def automation(self, ctx, state: str):
        state=state.lower()
        if state not in {"on","off"}: return await ctx.reply("Use `-automation on` or `-automation off`.")
        await ctx.reply(f"⚙️ Automation is now **{state.upper()}**.")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and not message.author.bot:
            urls=[a.url for a in message.attachments]
            self.deleted[message.channel.id]=(message.author,message.content,urls)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        gid=str(message.guild.id) if message.guild else ""
        # auto responder
        for trigger,response in self.autoreplies.get(gid,{}).items():
            if trigger in message.content.lower():
                try: await message.channel.send(response)
                except discord.HTTPException: pass
                break
        # tag reaction
        if self.bot.user and self.bot.user.mentioned_in(message):
            emoji=self.tag_reaction.get(gid)
            if emoji:
                try: await message.add_reaction(emoji)
                except discord.HTTPException: pass

async def setup(bot): await bot.add_cog(Automation(bot))
