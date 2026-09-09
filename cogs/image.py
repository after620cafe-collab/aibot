import io
import discord
from discord.ext import commands
from services.gemini import generate_image

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imagine", aliases=["image", "draw"])
    async def imagine(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                response = await generate_image(prompt)
                for part in response.candidates[0].content.parts:
                    if getattr(part, "inline_data", None):
                        data = part.inline_data.data
                        if isinstance(data, str):
                            import base64
                            data = base64.b64decode(data)
                        await ctx.reply(
                            content=f"🎨 Generated: **{prompt[:150]}**",
                            file=discord.File(io.BytesIO(data), filename="aqua-generated.png")
                        )
                        return
                text = getattr(response, "text", None)
                await ctx.reply(
                    "⚠️ Image generation isn't enabled for the configured Gemini model/account right now."
                    + (f"\nModel response: {text[:500]}" if text else "")
                )
            except Exception as e:
                await ctx.reply(f"⚠️ Image generation unavailable: `{type(e).__name__}`")

async def setup(bot):
    await bot.add_cog(Image(bot))
