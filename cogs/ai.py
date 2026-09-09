import os
import discord
from discord.ext import commands
from discord import app_commands
from services.groq_ai import ask, friendly_error
from services.memory import add, clear, format_history
from config import MAX_REPLY_CHARS

SYSTEM = """You are Rani AI, a polished Discord assistant made by Tyson.
Be natural, helpful, concise and friendly. Understand English, Hindi, Hinglish and Gujarati.
Never pretend to have performed an action you did not perform. Avoid huge walls of text.
"""

def key_for(ctx):
    return f"{ctx.guild.id if ctx.guild else 'dm'}:{ctx.author.id}"

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_ai(self, ctx, prompt, use_memory=True):
        key = key_for(ctx)
        history = format_history(key) if use_memory else ""
        messages = [{"role":"system","content":SYSTEM}]
        if history:
            for line in history.splitlines():
                if line.startswith("User: "):
                    messages.append({"role":"user","content":line[6:]})
                elif line.startswith("Rani AI: "):
                    messages.append({"role":"assistant","content":line[9:]})
        messages.append({"role":"user","content":prompt})
        async with ctx.typing():
            reply = await ask(messages)
        if use_memory:
            add(key, "User", prompt)
            add(key, "Rani AI", reply)
        return reply[:MAX_REPLY_CHARS]

    async def ai_reply(self, ctx, prompt):
        try:
            await ctx.reply(await self.run_ai(ctx, prompt), mention_author=False)
        except Exception as e:
            await ctx.reply(f"⚠️ **AI unavailable**\n{friendly_error(e)}", mention_author=False)

    @commands.command(name="ai", aliases=["ask", "chat", "gpt"])
    async def ai(self, ctx, *, prompt: str):
        await self.ai_reply(ctx, prompt)

    @app_commands.command(name="ai", description="Chat with Rani AI")
    @app_commands.describe(message="Your question or message")
    async def slash_ai(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True)
        class Ctx:
            guild = interaction.guild
            author = interaction.user
            def typing(self):
                class Dummy:
                    async def __aenter__(self): return self
                    async def __aexit__(self, *args): return False
                return Dummy()
            async def reply(self, *args, **kwargs):
                return await interaction.followup.send(*args, **kwargs)
        ctx = Ctx()
        try:
            result = await self.run_ai(ctx, message)
            await interaction.followup.send(result)
        except Exception as e:
            await interaction.followup.send(f"⚠️ **AI unavailable**\n{friendly_error(e)}")

    @commands.command(name="reset", aliases=["forget", "clearmemory"])
    async def reset(self, ctx):
        clear(key_for(ctx))
        await ctx.reply("🧠 Memory cleared. Fresh start!", mention_author=False)

    @commands.command(name="roast")
    async def roast(self, ctx, member: discord.Member | None = None):
        target = member or ctx.author
        await self.ai_reply(ctx, f"Give a short playful harmless roast for {target.display_name}.",)

    @commands.command(name="rizz")
    async def rizz(self, ctx, *, situation: str = "Give me a smooth cute opener."):
        await self.ai_reply(ctx, f"Create a short playful rizz reply for: {situation}")

    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, language: str, *, text: str):
        await self.ai_reply(ctx, f"Translate into {language}. Return only the translation.\n{text}")

    @commands.command(name="rewrite", aliases=["polish"])
    async def rewrite(self, ctx, style: str, *, text: str):
        await self.ai_reply(ctx, f"Rewrite this in {style} style. Return only the rewritten text.\n{text}")

    @commands.command(name="summarize", aliases=["summary"])
    async def summarize(self, ctx, *, text: str):
        await self.ai_reply(ctx, f"Summarize this in easy words with short bullet points:\n{text}")

    @commands.command(name="explain")
    async def explain(self, ctx, *, topic: str):
        await self.ai_reply(ctx, f"Explain this like I am a beginner, with a simple example: {topic}")

    @commands.command(name="code")
    async def code(self, ctx, *, request: str):
        await self.ai_reply(ctx, f"Help with this coding request. Give clean code and a short explanation: {request}")

    @commands.command(name="aihelp")
    async def aihelp(self, ctx):
        e = discord.Embed(title="🧠 Rani AI", description="AI + translation + text tools", color=discord.Color.red())
        e.add_field(name="Chat", value=f"`-ai <message>`\n`/ai <message>`", inline=False)
        e.add_field(name="Text", value="`-translate <language> <text>`\n`-rewrite <style> <text>`\n`-summarize <text>`\n`-explain <topic>`", inline=False)
        e.set_footer(text="Made by Tyson")
        await ctx.reply(embed=e, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = os.getenv("AI_AUTO_CHANNEL_ID", "").strip()
        if not channel_id or str(message.channel.id) != channel_id:
            return
        if message.content.startswith("-"):
            return
        if self.bot.user and self.bot.user.mentioned_in(message):
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()
            if prompt:
                try:
                    ctx = await self.bot.get_context(message)
                    reply = await self.run_ai(ctx, prompt)
                    await message.reply(reply, mention_author=False)
                except Exception:
                    pass

async def setup(bot):
    cog = AI(bot)
    await bot.add_cog(cog)
