import discord
from discord.ext import commands
import config
import sqlite3
from db import execute_query

class roles_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # When a role is created, this command will create a corresponding channel
    async def createRoleChannel(self, ctx, guild, role):
        category_name = config.CATEGORY_NAME 
        category = discord.utils.get(guild.categories, name = category_name)

        # Ensures that only people within a role/group can read their channels messages
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
    
    # This command will create a role for users to join
    @commands.command()
    async def create(self, ctx, roleName: str):
        guild = ctx.guild

        # Run check to see if the role name has already been used
        if discord.utils.get(guild.roles, name = f"{config.GROUP_PREFIX}{roleName}"):
            embed = discord.Embed(
                color = discord.Color.blurple(),
                title = "Sorry!",
                description = f'The role "{roleName}" has already been created'
            )
            embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
            await ctx.send(embed = embed)
            return
        
        # If the name has not been used, create the role
        role = await guild.create_role(name = f"{config.GROUP_PREFIX}{roleName}")
        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = "Success!",
            description = f'"{roleName}" has been created.'
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)
        await self.createRoleChannel(ctx, guild, role)
        #Add the role and its server to the database  
        execute_query('''
            INSERT INTO groups (id,group_name, server_id)
            VALUES (?, ?, ?);
        ''', (role.id, role.name, role.guild.id))

    # This command will delete a given role and its channel
    @commands.command()
    async def delete(self, ctx, roleName: str):
        guild = ctx.guild

        # Find the correct role and channel to delete
        role = discord.utils.get(guild.roles, name = f"{config.GROUP_PREFIX}{roleName}")
        if role is None:
            message = "Role not found!"
            await ctx.send(message=message)
            return
        channel = discord.utils.get(guild.text_channels, name = role.name)

        # Check whether or not this user can delete roles
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

        # Remove the role from the database
        execute_query('''
            DELETE FROM groups WHERE group_name = ? AND server_id = ?;
        ''', (role.name, guild.id))

    # This command will delete a given role and its channel
    @commands.command()
    async def leave(self, ctx, roleName: str):
        guild = ctx.guild
        # Find the correct role and channel to delete
        role = discord.utils.get(guild.roles, name = f"{config.GROUP_PREFIX}{roleName}")
        if role is None:
            message = "Role not found!"
            await ctx.send(message)
            return
        
        if role not in ctx.author.roles:
            message = f"You do not have the role '{roleName}' to leave the group."
            await ctx.send(message)
            return
    
        title = "Success!"
        message = "You have left the group"
        await ctx.author.remove_roles(role)

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = title,
            description = message
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)

        print(role.id,ctx.author.id)
        # Remove the role from the database
        execute_query('''
            DELETE FROM group_members WHERE group_id = ? AND user_id = ?;
        ''', (role.id, ctx.author.id))
    # List all the available roles for users to join
    @commands.command()
    async def listRoles(self, ctx):
        guild = ctx.guild

        # Loop through the roles within the server with the group prefix to ensure other roles are not listed
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

    # Allow a user to join a specified role
    @commands.command()
    async def join(self, ctx, role_name):
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=f"{config.GROUP_PREFIX}{role_name}")

        # Check if the role exists and if the user is already in the role
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
            # Add the user id and their role into the database, then add the user id and the user name
            execute_query('''
            INSERT OR IGNORE INTO users (id, username)
            VALUES (?,?);
            ''', (ctx.author.id, ctx.author.name))
            execute_query('''
            INSERT INTO group_members (group_id, user_id)
            VALUES (?, ?);
            ''', (role.id, ctx.author.id))

        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = title,
            description = description
        )

        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
        await ctx.send(embed = embed)
async def setup(bot):
    await bot.add_cog(roles_commands(bot))