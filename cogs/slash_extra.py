import discord
from discord import app_commands
from discord.ext import commands

RED = discord.Color.from_rgb(220, 35, 55)

class SlashExtra(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ping", description="Check Rani latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 **Rani Pong!** `{round(self.bot.latency*1000)}ms`")

    @app_commands.command(name="help", description="Open Rani's professional help menu")
    async def help_cmd(self, interaction: discord.Interaction):
        e=discord.Embed(title="🔴 RANI AI • HELP CENTER",description="**Rani AI — All-in-One Discord Bot**\n\n🎵 Music • 🧠 AI Chat • 🛡️ Moderation • 🎙️ Voice • ⚙️ Automation • 🎭 Roles",color=RED)
        e.add_field(name="🧠 AI",value="`/ai` • `-ai` • translate • rewrite • summarize • explain • code",inline=False)
        e.add_field(name="🎵 Music",value="`/play` • `/pause` • `/resume` • `/skip` • `/queue` • `-247 on`",inline=False)
        e.add_field(name="🛡️ Moderation",value="Ban • Kick • Warn • Timeout • Lock • Clear • Hide",inline=False)
        e.add_field(name="🎙️ Voice",value="Join • TTS • Voice moderation",inline=False)
        e.set_footer(text="Rani AI • Created by Tyson")
        await interaction.response.send_message(embed=e)

async def setup(bot):
    await bot.add_cog(SlashExtra(bot))
