import discord
from discord.ext import commands

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        role = await guild.create_role(name = roleName)
        await ctx.send(f'"{roleName}" has been created.')

        await self.createRoleChannel(ctx, role)

    async def createRoleChannel(ctx, role: discord.Role):
        guild = ctx.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False),
            role: discord.PermissionOverwrite(read_messages = True)
        }

        print("hello")
        channelName = f'standup-bot-group-{role.name}'
        channel = await guild.create_text_channel(channelName, overwrites=overwrites)
        await ctx.send(f'"{role.name}" channel has been created.')

    @commands.command()
    async def help(self, ctx):
        message = """
        Here are the available commands:
            .addRole - Create a new role for a group

        """
        await ctx.send(message)



async def setup(bot):
    await bot.add_cog(general_commands(bot))