import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="8ball")
    async def eightball(self, ctx, *, question: str):
        answers = ["Yes.", "No.", "Maybe.", "Definitely.", "Ask again later.", "Absolutely not.", "Looks good."]
        await ctx.reply(f"🎱 **{random.choice(answers)}**", mention_author=False)

    @commands.hybrid_command(name="coinflip")
    async def coinflip(self, ctx):
        await ctx.reply(f"🪙 **{random.choice(['Heads', 'Tails'])}**", mention_author=False)

    @commands.hybrid_command(name="dice")
    async def dice(self, ctx, sides: int = 6):
        sides = max(2, min(sides, 100))
        await ctx.reply(f"🎲 You rolled **{random.randint(1, sides)} / {sides}**", mention_author=False)

    @commands.hybrid_command(name="rps")
    async def rps(self, ctx, choice: str):
        choice = choice.lower()
        if choice not in {"rock","paper","scissors"}:
            return await ctx.reply("Use `rock`, `paper`, or `scissors`.")
        bot = random.choice(["rock","paper","scissors"])
        win = (choice, bot) in {("rock","scissors"),("paper","rock"),("scissors","paper")}
        result = "You win! 🔥" if win else ("Draw! 🤝" if choice == bot else "I win! 😈")
        await ctx.reply(f"🎮 You: **{choice}** | Me: **{bot}**\n{result}", mention_author=False)

    @commands.hybrid_command(name="joke")
    async def joke(self, ctx):
        jokes = [
            "Why did the bot go to school? To improve its byte-sized knowledge. 🤖",
            "I told my server a joke. It needed more bandwidth. 😂",
            "Why was the Discord bot calm? It had excellent channel control. 😎",
        ]
        await ctx.reply(random.choice(jokes), mention_author=False)

    @commands.hybrid_command(name="truth")
    async def truth(self, ctx):
        await ctx.reply("😳 Truth: What is your most embarrassing autocorrect?", mention_author=False)

    @commands.hybrid_command(name="dare")
    async def dare(self, ctx):
        await ctx.reply("🔥 Dare: Send the last emoji you used 10 times.", mention_author=False)

    @commands.hybrid_command(name="choose")
    async def choose(self, ctx, *, options: str):
        vals = [x.strip() for x in options.split("|") if x.strip()]
        if len(vals) < 2: return await ctx.reply("Use: `-choose pizza | burger | pasta`")
        await ctx.reply(f"🎯 I choose: **{random.choice(vals)}**", mention_author=False)

    @commands.hybrid_command(name="rate")
    async def rate(self, ctx, *, thing: str):
        await ctx.reply(f"📊 **{thing}** gets **{random.randint(1,100)}%**", mention_author=False)

async def setup(bot):
    await bot.add_cog(Fun(bot))
