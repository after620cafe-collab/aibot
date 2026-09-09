import discord
from discord.ext import commands

class RoleButton(discord.ui.Button):
    def __init__(self, role_id):
        super().__init__(label="Get Role", emoji="🎟️", style=discord.ButtonStyle.danger, custom_id=f"rr:{role_id}")
        self.role_id=role_id
    async def callback(self, interaction: discord.Interaction):
        role=interaction.guild.get_role(self.role_id)
        if not role: return await interaction.response.send_message("❌ Role no longer exists.", ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason="Reaction role toggle")
            return await interaction.response.send_message(f"➖ Removed {role.mention}.", ephemeral=True)
        await interaction.user.add_roles(role, reason="Reaction role toggle")
        await interaction.response.send_message(f"➕ Added {role.mention}.", ephemeral=True)

class RolePanel(discord.ui.View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.add_item(RoleButton(role_id))

class Roles(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @commands.command(name="createrole")
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, *, name: str):
        role=await ctx.guild.create_role(name=name, reason=f"Created by {ctx.author}")
        await ctx.reply(f"🎭 Created {role.mention}.", mention_author=False)

    @commands.command(name="deleterole")
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, role: discord.Role):
        if role >= ctx.guild.me.top_role: return await ctx.reply("❌ That role is above my role.")
        await role.delete(reason=f"Deleted by {ctx.author}")
        await ctx.reply("🗑️ Role deleted.", mention_author=False)

    @commands.command(name="giverole", aliases=["role"])
    @commands.has_permissions(manage_roles=True)
    async def giverole(self, ctx, member: discord.Member, role: discord.Role):
        if role >= ctx.guild.me.top_role: return await ctx.reply("❌ Move my bot role above that role.")
        await member.add_roles(role, reason=f"Given by {ctx.author}")
        await ctx.reply(f"🎭 Added {role.mention} to {member.mention}.", mention_author=False)

    @commands.command(name="removerole", aliases=["rrole"])
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role, reason=f"Removed by {ctx.author}")
        await ctx.reply(f"🎭 Removed {role.mention} from {member.mention}.", mention_author=False)

    @commands.command(name="reactionrole", aliases=["rr"])
    @commands.has_permissions(manage_roles=True)
    async def reactionrole(self, ctx, role: discord.Role):
        if role >= ctx.guild.me.top_role:
            return await ctx.reply("❌ Move my bot role above that role.")
        e=discord.Embed(title="🎟️ Reaction Role", description=f"Click the button below to toggle {role.mention}.", color=discord.Color.red())
        e.set_footer(text="Rani AI • Made by Tyson")
        await ctx.send(embed=e, view=RolePanel(role.id))

    @commands.command(name="rolecolor")
    @commands.has_permissions(manage_roles=True)
    async def rolecolor(self, ctx, role: discord.Role, hex_color: str):
        try: color=discord.Color(int(hex_color.replace("#",""),16))
        except ValueError: return await ctx.reply("❌ Example: `-rolecolor @Role #ff0000`")
        await role.edit(color=color)
        await ctx.reply("🎨 Role color updated.", mention_author=False)

async def setup(bot): await bot.add_cog(Roles(bot))
