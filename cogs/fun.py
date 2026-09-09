import random
import discord
from discord.ext import commands
from services.gemini import ask

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", aliases=["eightball"])
    async def eightball(self, ctx, *, question: str):
        answers = [
            "Definitely yes. 😎", "No chance bro 💀", "Ask me again later.",
            "The vibes say YES.", "Probably... 👀", "My AI crystal ball is confused 😂"
        ]
        await ctx.reply(random.choice(answers))

    @commands.command(name="coinflip", aliases=["coin"])
    async def coin(self, ctx):
        await ctx.reply(random.choice(["🪙 Heads!", "🪙 Tails!"]))

    @commands.command(name="dice", aliases=["roll"])
    async def dice(self, ctx, sides: int = 6):
        sides = max(2, min(sides, 1000))
        await ctx.reply(f"🎲 You rolled **{random.randint(1, sides)}** / {sides}")

    @commands.command(name="rps")
    async def rps(self, ctx, choice: str):
        choice = choice.lower()
        options = ["rock", "paper", "scissors"]
        if choice not in options:
            return await ctx.reply("Use `-rps rock`, `-rps paper`, or `-rps scissors`.")
        bot = random.choice(options)
        if choice == bot:
            result = "Draw 😎"
        elif (choice, bot) in [("rock","scissors"),("paper","rock"),("scissors","paper")]:
            result = "You win! 🔥"
        else:
            result = "I win 😈"
        await ctx.reply(f"You: **{choice}** | Me: **{bot}**\n{result}")

    @commands.command(name="joke")
    async def joke(self, ctx):
        try:
            joke = await ask("Tell one short, clean, genuinely funny joke. No explanation.")
        except Exception:
            joke = "Why did the bot go to school? To improve its byte-sized knowledge. 🤖"
        await ctx.reply(joke)

    @commands.command(name="ship")
    async def ship(self, ctx, a: discord.Member, b: discord.Member):
        score = random.randint(0, 100)
        await ctx.reply(f"💘 **{a.display_name} × {b.display_name}** = **{score}%** compatibility.")

    @commands.command(name="truth")
    async def truth(self, ctx):
        prompts = ["What is your most embarrassing autocorrect?", "Who was your last crush?", "What's one secret talent you have?"]
        await ctx.reply("🫣 Truth: " + random.choice(prompts))

    @commands.command(name="dare")
    async def dare(self, ctx):
        prompts = ["Send the funniest sticker you have.", "Change your nickname to something silly for 5 minutes.", "Type your next message with only emojis."]
        await ctx.reply("😈 Dare: " + random.choice(prompts))

async def setup(bot):
    await bot.add_cog(Fun(bot))
