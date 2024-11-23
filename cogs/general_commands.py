import discord
from discord.ext import commands

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # List all available commands for users to use
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = "Here Are The Available Commands:",
            description = ".create - Create a new role for a group \n"
                        ".listRole - List all available roles for a user to join \n"
                        ".join - Add user to a specified role \n"
                        ".delete - Delete role and its channel \n"
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")

        await ctx.send(embed = embed)

async def setup(bot):
    await bot.add_cog(general_commands(bot))