import asyncio
import discord
from discord.ext import commands

class NitroView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=30)
        self.owner_id=owner_id

    @discord.ui.button(label="🎁 Claim Nitro", style=discord.ButtonStyle.danger)
    async def claim(self, interaction, button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("❌ This prank belongs to the command user.", ephemeral=True)
        await interaction.response.edit_message(content="🌀 **Claiming Nitro...**", embed=None, view=None)
        for text in ["🌀 Connecting to Discord...", "🔴 Verifying gift...", "🎁 Preparing Nitro...", "✨ Almost done..."]:
            await asyncio.sleep(0.7)
            try: await interaction.edit_original_response(content=text)
            except discord.HTTPException: pass
        e=discord.Embed(title="😂 NITRO PRANK", description="You got **pranked**. No payment, login or link was collected.", color=discord.Color.red())
        e.set_footer(text="Safe prank • Made by Tyson")
        await interaction.edit_original_response(content=None, embed=e, view=None)

class Prank(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @commands.hybrid_command(name="nitro")
    async def nitro(self, ctx):
        e=discord.Embed(title="💎 Discord Nitro Gift", description="🎁 Someone sent you a Nitro gift!\n\nClick the button to start the claim animation.", color=discord.Color.red())
        e.add_field(name="Status", value="🟢 Gift detected", inline=False)
        e.set_footer(text="PRANK • Made by Tyson")
        await ctx.send(embed=e, view=NitroView(ctx.author.id))

async def setup(bot): await bot.add_cog(Prank(bot))
