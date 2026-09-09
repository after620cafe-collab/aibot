import os
import discord
from discord.ext import commands
from services.gemini import ask, friendly_error
from services.memory import add, clear, format_history

SYSTEM = """You are Aqua AI, a polished Discord assistant made by Tyson.
Be helpful, natural and concise. Match English, Hindi, Hinglish or Gujarati.
Use clean Discord-friendly formatting. Do not claim actions you did not perform.
"""

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_ai(self, ctx, prompt, use_memory=True):
        key = f"{ctx.guild.id if ctx.guild else 'dm'}:{ctx.author.id}"
        history = format_history(key) if use_memory else ""
        full = f"{SYSTEM}\nConversation history:\n{history}\n\nUser: {prompt}"
        async with ctx.typing():
            reply = await ask(full)
        if use_memory:
            add(key, "User", prompt)
            add(key, "Aqua AI", reply)
        return reply

    @commands.command(name="ai", aliases=["ask", "chat", "gpt"])
    async def ai(self, ctx, *, prompt: str):
        try:
            await ctx.reply(await self.run_ai(ctx, prompt), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ **AI unavailable**\n{friendly_error(e)}", mention_author=False)

    @commands.command(name="reset", aliases=["forget", "clearmemory"])
    async def reset(self, ctx):
        key = f"{ctx.guild.id if ctx.guild else 'dm'}:{ctx.author.id}"
        clear(key)
        await ctx.reply("🧠 **Memory cleared.** Fresh start!", mention_author=False)

    @commands.command(name="roast")
    async def roast(self, ctx, member: discord.Member | None = None):
        target = member or ctx.author
        try:
            await ctx.reply(await self.run_ai(ctx, f"Give a short playful harmless roast for {target.display_name}.", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="rizz")
    async def rizz(self, ctx, *, situation: str = "Give me a smooth, cute opener."):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Create a short playful rizz reply for: {situation}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, language: str, *, text: str):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Translate into {language}. Return only the translation.\n{text}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="rewrite", aliases=["polish"])
    async def rewrite(self, ctx, style: str, *, text: str):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Rewrite this in a {style} style. Return only the rewritten text.\n{text}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="summarize", aliases=["summary"])
    async def summarize(self, ctx, *, text: str):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Summarize this in very easy words with short bullet points:\n{text}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="explain")
    async def explain(self, ctx, *, topic: str):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Explain this topic like I am a beginner, with a simple example: {topic}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.command(name="code")
    async def code(self, ctx, *, request: str):
        try:
            await ctx.reply(await self.run_ai(ctx, f"Help with this coding request. Give clean code and a short explanation: {request}", False), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ {friendly_error(e)}", mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = os.getenv("AI_AUTO_CHANNEL_ID", "").strip()
        if not channel_id or str(message.channel.id) != channel_id:
            return
        if message.content.startswith(("-", "!")):
            return
        if self.bot.user and self.bot.user.mentioned_in(message):
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()
            if prompt:
                try:
                    reply = await self.run_ai(message, prompt)
                    await message.reply(reply, mention_author=False)
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(AI(bot))
