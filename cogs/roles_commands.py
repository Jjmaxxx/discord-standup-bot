import discord
from discord.ext import commands
import config
class roles_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def createRoleChannel(self, ctx,guild,role):
        category_name = config.CATEGORY_NAME 
        category = discord.utils.get(guild.categories, name=category_name)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False),
            role: discord.PermissionOverwrite(read_messages = True)
        }
        channel_name = role.name
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
        await ctx.send(f'"{role.name}" channel has been created')
        
    @commands.command()
    async def createRole(self, ctx, roleName: str):
        guild = ctx.guild
        # if len(roleName) < 1:
        #     await ctx.send("You need to include a role name.")
        
        #Run check to see if the role name has already been used
        if discord.utils.get(guild.roles, name = roleName):
            await ctx.send(f'The role "{roleName}" has already been created.')
            return
        
        #If the name has not been used, create the role
        role = await guild.create_role(name = f"{config.GROUP_PREFIX}{roleName}")
        await ctx.send(f'"{roleName}" has been created.')
        await self.createRoleChannel(ctx,guild,role)
    
    @commands.command()
    async def listRoles(self, ctx):
        guild = ctx.guild
        matching_roles = [role for role in guild.roles if role.name.startswith(config.GROUP_PREFIX)]
        if matching_roles:
            message = "\n".join(role.name[len(config.GROUP_PREFIX):] for role in matching_roles)
        else:
            message = "No roles found starting with the specified prefix."        
        await ctx.send(message)
    @commands.command()
    async def addUserRole(self, ctx, role_name):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=f"{config.GROUP_PREFIX}{role_name}")
        if role is None:
            await ctx.send(f'Role "{role_name}" does not exist.')
            return
        if role in ctx.author.roles:
            await ctx.send(f'You already have the role "{role_name}".')
            return
        await ctx.author.add_roles(role)
        await ctx.send(f'Role "{role_name}" has been added to you!')

        

async def setup(bot):
    await bot.add_cog(roles_commands(bot))