import discord
from discord.ext import commands

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        message = """
        Here are the available commands:
            .addRole - Create a new role for a group

        """
        await ctx.send(message)



async def setup(bot):
    await bot.add_cog(general_commands(bot))