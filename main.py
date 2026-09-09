import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
PREFIX = os.getenv("PREFIX", "-")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Add it in Railway Variables.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
intents.reactions = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=intents,
    help_command=None,
    case_insensitive=True,
    strip_after_prefix=True,
)

EXTENSIONS = [
    "cogs.ai",
    "cogs.fun",
    "cogs.moderation",
    "cogs.automation",
    "cogs.roles",
    "cogs.utility",
    "cogs.prank",
    "cogs.voice",
    "cogs.music",
]

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"Rani AI ONLINE: {bot.user} ({bot.user.id})")
    print(f"Prefix: {PREFIX} | Servers: {len(bot.guilds)}")
    print("=" * 50)
    try:
        synced = await bot.tree.sync()
        print(f"Global slash commands synced: {len(synced)}")
        # Also sync into every connected guild so slash commands appear immediately,
        # instead of waiting for global Discord propagation.
        for guild in bot.guilds:
            try:
                bot.tree.copy_global_to(guild=guild)
                guild_synced = await bot.tree.sync(guild=guild)
                print(f"Guild slash sync: {guild.name} -> {len(guild_synced)}")
            except Exception:
                logging.exception("Guild slash sync failed for %s", guild.name)
    except Exception:
        logging.exception("Slash sync failed")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        return await ctx.reply("🛡️ You don't have the required permission.", mention_author=False)
    if isinstance(error, commands.BotMissingPermissions):
        return await ctx.reply("⚠️ I don't have the required Discord permission.", mention_author=False)
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.reply(f"❌ Missing argument: `{error.param.name}`", mention_author=False)
    if isinstance(error, commands.BadArgument):
        return await ctx.reply("❌ I couldn't understand that user/argument.", mention_author=False)
    logging.exception("Command error", exc_info=error)
    await ctx.reply("⚠️ Something went wrong. Check Railway logs.", mention_author=False)

async def load_extensions():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            print(f"Loaded: {ext}")
        except Exception:
            logging.exception("Could not load %s", ext)

async def runner():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(runner())
