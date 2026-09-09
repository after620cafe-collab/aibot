import os
import asyncio
import logging
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "-")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Add it in Railway Variables.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=intents,
    help_command=None,
    case_insensitive=True,
)

EXTENSIONS = [
    "cogs.ai",
    "cogs.fun",
    "cogs.moderation",
    "cogs.utility",
    "cogs.image",
    "cogs.voice",
]

@bot.event
async def on_ready():
    print("=" * 42)
    print(f"Aqua AI ONLINE: {bot.user} ({bot.user.id})")
    print(f"Prefix: {PREFIX}")
    print(f"Servers: {len(bot.guilds)}")
    print("=" * 42)
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        logging.exception("Slash sync failed: %s", e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission for that.")
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: `{error.param.name}`")
        return
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required Discord permission.")
        return
    logging.exception("Command error", exc_info=error)
    await ctx.send("⚠️ Something went wrong. Check the bot logs.")

async def load_extensions():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            print(f"Loaded: {ext}")
        except Exception as e:
            print(f"Could not load {ext}: {e}")

async def runner():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(runner())
