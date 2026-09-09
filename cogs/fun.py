import random
import discord
from discord.ext import commands
from services.gemini import ask

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", aliases=["eightball"])
    async def eightball(self, ctx, *, question: str):
        await ctx.reply(random.choice(["Definitely yes. 😎", "No chance bro 💀", "Ask me again later.", "The vibes say YES. 👀", "Probably...", "My crystal ball needs Wi-Fi 😂"]), mention_author=False)

    @commands.command(name="coinflip", aliases=["coin"])
    async def coin(self, ctx):
        await ctx.reply(random.choice(["🪙 **Heads!**", "🪙 **Tails!**"]), mention_author=False)

    @commands.command(name="dice", aliases=["roll"])
    async def dice(self, ctx, sides: int = 6):
        sides = max(2, min(sides, 1000))
        await ctx.reply(f"🎲 You rolled **{random.randint(1, sides)}** / {sides}", mention_author=False)

    @commands.command(name="rps")
    async def rps(self, ctx, choice: str):
        choice = choice.lower(); options = ["rock", "paper", "scissors"]
        if choice not in options:
            return await ctx.reply("Use `-rps rock`, `-rps paper`, or `-rps scissors`.", mention_author=False)
        bot = random.choice(options)
        result = "Draw 😎" if choice == bot else ("You win! 🔥" if (choice, bot) in [("rock","scissors"),("paper","rock"),("scissors","paper")] else "I win 😈")
        await ctx.reply(f"You: **{choice}** | Me: **{bot}**\n**{result}**", mention_author=False)

    @commands.command(name="joke")
    async def joke(self, ctx):
        try: text = await ask("Tell one short, clean, genuinely funny joke. No explanation.")
        except Exception: text = "Why did the bot go to school? To improve its byte-sized knowledge. 🤖"
        await ctx.reply(f"😂 {text}", mention_author=False)

    @commands.command(name="ship")
    async def ship(self, ctx, a: discord.Member, b: discord.Member):
        await ctx.reply(f"💘 **{a.display_name} × {b.display_name}** = **{random.randint(0,100)}%** compatibility.", mention_author=False)

    @commands.command(name="rate")
    async def rate(self, ctx, *, thing: str):
        await ctx.reply(f"📈 I'd rate **{thing}** a solid **{random.randint(1,10)}/10** 😎", mention_author=False)

    @commands.command(name="choose")
    async def choose(self, ctx, *, options: str):
        items = [x.strip() for x in options.split("|") if x.strip()]
        if len(items) < 2: return await ctx.reply("Use `-choose pizza | burger | pasta`", mention_author=False)
        await ctx.reply(f"🎯 I choose **{random.choice(items)}**", mention_author=False)

    @commands.command(name="compliment")
    async def compliment(self, ctx, member: discord.Member | None = None):
        member = member or ctx.author
        await ctx.reply(f"💖 {member.mention}, you're genuinely a vibe. Keep shining! ✨", mention_author=False)

    @commands.command(name="pickup")
    async def pickup(self, ctx):
        lines = ["Are you Wi-Fi? Because I’m feeling a connection. 📶❤️", "You must be a notification, because you just made my day. 😌", "I had a clever line, but then you smiled and I forgot it. 😭❤️"]
        await ctx.reply(random.choice(lines), mention_author=False)

    @commands.command(name="truth")
    async def truth(self, ctx):
        await ctx.reply("🫣 **Truth:** " + random.choice(["What's your most embarrassing autocorrect?", "What's one secret talent you have?", "Who was your last crush?"]), mention_author=False)

    @commands.command(name="dare")
    async def dare(self, ctx):
        await ctx.reply("😈 **Dare:** " + random.choice(["Send the funniest sticker you have.", "Change your nickname to something silly for 5 minutes.", "Type your next message using only emojis."]), mention_author=False)

async def setup(bot):
    await bot.add_cog(Fun(bot))
