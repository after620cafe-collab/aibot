import os
import discord
from discord.ext import commands
from services.gemini import ask
from services.memory import add, clear, format_history

SYSTEM = """You are Aqua AI, a friendly Discord assistant.
Reply naturally and concisely. The user may speak Hinglish, Hindi, Gujarati or English.
Match the user's language. You can be funny when appropriate, but never be abusive or threatening.
Do not claim to have performed actions you did not perform."""

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ai", aliases=["ask", "chat", "gpt"])
    async def ai(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                key = f"{ctx.guild.id if ctx.guild else 'dm'}:{ctx.author.id}"
                history = format_history(key)
                full = f"{SYSTEM}\nConversation history:\n{history}\n\nUser: {prompt}"
                reply = await ask(full)
                add(key, "User", prompt)
                add(key, "Aqua AI", reply)
                await ctx.reply(reply, mention_author=False)
            except Exception as e:
                await ctx.reply(f"⚠️ AI unavailable right now: `{type(e).__name__}`")

    @commands.command(name="reset", aliases=["forget", "clearmemory"])
    async def reset(self, ctx):
        key = f"{ctx.guild.id if ctx.guild else 'dm'}:{ctx.author.id}"
        clear(key)
        await ctx.reply("🧠 Memory cleared. Fresh start!")

    @commands.command(name="roast")
    async def roast(self, ctx, member: discord.Member | None = None):
        target = member or ctx.author
        async with ctx.typing():
            reply = await ask(f"{SYSTEM}\nGive a short playful roast for {target.display_name}. Keep it harmless.")
        await ctx.reply(reply)

    @commands.command(name="rizz")
    async def rizz(self, ctx, *, situation: str = "Give me a smooth, cute opener."):
        async with ctx.typing():
            reply = await ask(f"{SYSTEM}\nCreate a short playful rizz reply for this situation: {situation}")
        await ctx.reply(reply)

    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, language: str, *, text: str):
        async with ctx.typing():
            reply = await ask(f"{SYSTEM}\nTranslate the following text into {language}. Return only the translation.\n{text}")
        await ctx.reply(reply)

    @commands.command(name="rewrite", aliases=["polish"])
    async def rewrite(self, ctx, style: str, *, text: str):
        async with ctx.typing():
            reply = await ask(f"{SYSTEM}\nRewrite this text in a {style} style. Return only the rewritten text.\n{text}")
        await ctx.reply(reply)

    @commands.command(name="summarize", aliases=["summary"])
    async def summarize(self, ctx, *, text: str):
        async with ctx.typing():
            reply = await ask(f"{SYSTEM}\nSummarize this in easy words and bullet points:\n{text}")
        await ctx.reply(reply)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = os.getenv("AI_AUTO_CHANNEL_ID")
        if not channel_id or str(message.channel.id) != channel_id:
            return
        if message.content.startswith(("-", "!")):
            return
        if self.bot.user and self.bot.user.mentioned_in(message):
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if prompt:
                try:
                    async with message.channel.typing():
                        reply = await ask(f"{SYSTEM}\nUser says: {prompt}")
                    await message.reply(reply, mention_author=False)
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(AI(bot))
