import io
import base64
import discord
from discord.ext import commands
from services.gemini import generate_image, friendly_error

class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imagine", aliases=["image", "draw"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def imagine(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                response = await generate_image(prompt)
                candidates = getattr(response, "candidates", []) or []
                if candidates:
                    parts = getattr(candidates[0].content, "parts", []) or []
                    for part in parts:
                        inline = getattr(part, "inline_data", None)
                        if inline:
                            data = inline.data
                            if isinstance(data, str):
                                data = base64.b64decode(data)
                            file = discord.File(io.BytesIO(data), filename="aqua-generated.png")
                            e = discord.Embed(title="🎨 Aqua AI Image", description=f"**Prompt:** {prompt[:800]}", color=discord.Color.blurple())
                            e.set_footer(text="Made by Tyson • Gemini Image")
                            return await ctx.reply(embed=e, file=file, mention_author=False)
                raise RuntimeError("The image model returned no image data")
            except Exception as e:
                await ctx.reply(f"⚠️ **Image generation failed**\n{friendly_error(e)}", mention_author=False)

    @imagine.error
    async def imagine_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"⏳ Try again in **{error.retry_after:.0f}s**.", mention_author=False)

async def setup(bot):
    await bot.add_cog(Image(bot))
