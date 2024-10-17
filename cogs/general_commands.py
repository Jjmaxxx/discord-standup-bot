import discord
from discord.ext import commands

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def idk(self, ctx):
        message = """
            idk
        """
        await ctx.send(message)

    @commands.command()
    async def help(self, ctx):
        message = """
        Here are the available commands:
            #help` - Displays Commands!
        """
        await ctx.send(message)



async def setup(bot):
    await bot.add_cog(general_commands(bot))