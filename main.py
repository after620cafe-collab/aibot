import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
PREFIX = os.getenv("PREFIX", "-")
SYNC_GUILD_ID = os.getenv("SYNC_GUILD_ID", "").strip()

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
    "cogs.fun", "cogs.moderation", "cogs.automation",
    "cogs.roles", "cogs.utility", "cogs.prank", "cogs.voice", "cogs.music",
]

@bot.event
async def on_ready():
    logging.info("Rani ONLINE: %s (%s) | prefix=%s | guilds=%s", bot.user, bot.user.id, PREFIX, len(bot.guilds))
    try:
        if SYNC_GUILD_ID.isdigit():
            guild = discord.Object(id=int(SYNC_GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logging.info("Guild slash sync OK: %s commands -> %s", len(synced), SYNC_GUILD_ID)
        else:
            synced = await bot.tree.sync()
            logging.info("Global slash sync OK: %s commands", len(synced))
    except Exception:
        logging.exception("Slash sync failed. Invite bot with applications.commands scope and set SYNC_GUILD_ID for instant sync.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    if isinstance(error, commands.MissingPermissions): return await ctx.reply("🛡️ You don't have the required permission.", mention_author=False)
    if isinstance(error, commands.BotMissingPermissions): return await ctx.reply("⚠️ I don't have the required Discord permission.", mention_author=False)
    if isinstance(error, commands.MissingRequiredArgument): return await ctx.reply(f"❌ Missing argument: `{error.param.name}`", mention_author=False)
    if isinstance(error, commands.BadArgument): return await ctx.reply("❌ I couldn't understand that user/argument.", mention_author=False)
    logging.exception("Command error", exc_info=error)
    try: await ctx.reply("⚠️ Something went wrong. Check Railway logs.", mention_author=False)
    except Exception: pass

async def load_extensions():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            logging.info("Loaded: %s", ext)
        except Exception:
            logging.exception("Could not load %s", ext)

async def runner():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(runner())
