import asyncio
import discord
from discord.ext import commands

RED = discord.Color.from_rgb(220, 35, 55)


class NitroClaimView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=45)
        self.owner_id = owner_id

    @discord.ui.button(label="🎁  Claim Nitro", style=discord.ButtonStyle.danger, custom_id="rani:nitro:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(
                "🔒 Only the person who started this prank can press this button.",
                ephemeral=True,
            )

        await interaction.response.defer()
        stages = [
            ("🔴 RANI NITRO", "Connecting to Discord gift service…", "🟡 Checking gift"),
            ("🔴 RANI NITRO", "Verifying gift package…", "🟠 Verifying"),
            ("🔴 RANI NITRO", "Preparing your Nitro animation…", "🔵 Preparing"),
            ("🔴 RANI NITRO", "Almost there…", "🟢 Finalizing"),
        ]
        for title, desc, status in stages:
            embed = discord.Embed(title=title, description=f"**{desc}**", color=RED)
            embed.add_field(name="STATUS", value=f"`{status}`", inline=False)
            embed.add_field(name="PROGRESS", value="▰▰▰▰▱▱▱▱  60%", inline=False)
            embed.set_footer(text="Rani • Made by Tyson")
            try:
                await interaction.edit_original_response(embed=embed, view=None)
            except discord.HTTPException:
                pass
            await asyncio.sleep(0.9)

        final = discord.Embed(
            title="🎁  NITRO GIFT",
            description=(
                "### 😂 You got pranked!\n"
                "This was a **Nitro-style visual prank** by Rani.\n\n"
                "No login, password, payment or external claim link was requested."
            ),
            color=RED,
        )
        final.add_field(name="💎 Discord Nitro", value="**PRANK COMPLETE**", inline=False)
        final.set_footer(text="Rani AI • Made by Tyson")
        await interaction.edit_original_response(embed=final, view=None)


class Prank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nitro", aliases=["nitroprank"])
    async def nitro(self, ctx):
        embed = discord.Embed(
            title="🎁  Discord Nitro Gift",
            description=(
                "**Someone sent you a Nitro gift!**\n\n"
                "A premium-style claim animation is ready.\n"
                "Press the button below to continue."
            ),
            color=RED,
        )
        embed.add_field(name="💎 Gift", value="Discord Nitro", inline=True)
        embed.add_field(name="🟢 Status", value="Gift detected", inline=True)
        embed.add_field(name="🎁 Type", value="Nitro-style prank", inline=True)
        embed.set_footer(text="Rani AI • Made by Tyson")
        await ctx.send(embed=embed, view=NitroClaimView(ctx.author.id))


async def setup(bot):
    await bot.add_cog(Prank(bot))
