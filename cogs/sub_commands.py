import discord
from discord.ext import commands

class sub_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def createRoleChannel(self, ctx, role: discord.Role):
        guild = ctx.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False),
            role: discord.PermissionOverwrite(read_messages = True)
        }

        channelName = f'standup-bot-group-{role.name}'
        channel = await guild.create_text_channel(channelName, overwrites=overwrites)
        await ctx.send(f'"{role.name}" channel has been created.')

async def setup(bot):
    await bot.add_cog(sub_commands(bot))