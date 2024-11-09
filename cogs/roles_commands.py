import discord
from discord.ext import commands
import config
class roles_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def createRoleChannel(self, ctx, guild, role):
        category_name = config.CATEGORY_NAME 
        category = discord.utils.get(guild.categories, name = category_name)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False),
            role: discord.PermissionOverwrite(read_messages = True)
        }

        channelName = role.name
        channel = await guild.create_text_channel(channelName, overwrites = overwrites, category = category)

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = "Success!",
            description = f'"{role.name}" channel has been created'
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)
        
    @commands.command()
    async def createRole(self, ctx, roleName: str):
        guild = ctx.guild
        # if len(roleName) < 1:
        #     await ctx.send("You need to include a role name.")
        
        #Run check to see if the role name has already been used
        if discord.utils.get(guild.roles, name = roleName):
            embed = discord.Embed(
                color = discord.Color.blurple(),
                title = "Sorry!",
                description = f'The role "{roleName}" has already been created'
            )
            embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
            await ctx.send(embed = embed)
            return
        
        #If the name has not been used, create the role
        role = await guild.create_role(name = f"{config.GROUP_PREFIX}{roleName}")
        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = "Success!",
            description = f'"{roleName}" has been created.'
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)
        await self.createRoleChannel(ctx, guild, role)
    
    @commands.command()
    async def deleteRole(self, ctx, roleName: str):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name = roleName)
        channel = discord.utils.get(guild.text_channels, name = role.name)
        if ctx.author.top_role <= role:
            title = "Sorry!"
            message = "You do not have permission to delete this role"
        else: 
            title = "Success!"
            message = "The role has been deleted"
            await channel.delete()
            await role.delete()

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = title,
            description = message
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)

    @commands.command()
    async def listRoles(self, ctx):
        guild = ctx.guild
        matching_roles = [role for role in guild.roles if role.name.startswith(config.GROUP_PREFIX)]
        if matching_roles:
            message = "\n".join(role.name[len(config.GROUP_PREFIX):] for role in matching_roles)
            title = "Here Are The Existing Roles:"
        else:
            message = "No roles found starting with the specified prefix."
            title = "Sorry!"

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = title,
            description = message
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")      
        await ctx.send(embed = embed)

    @commands.command()
    async def addUserRole(self, ctx, role_name):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=f"{config.GROUP_PREFIX}{role_name}")
        if role is None:
            title = "Sorry!"
            description = f'Role "{role_name}" does not exist.'

        elif role in ctx.author.roles:
            title = "Sorry!",
            description = f'You already have the role "{role_name}".'

        else:
            title = "Success!"
            description = f'Role "{role_name}" has been added to you!'
            await ctx.author.add_roles(role)

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = title,
            description = description
        )

        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)

        

async def setup(bot):
    await bot.add_cog(roles_commands(bot))