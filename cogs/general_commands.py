from discord.ext import commands
from config import client
from utils import send_embed

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # List all available commands for users to use
    @commands.command()
    async def help(self, ctx):
        title = "Here Are The Available Commands:"
        description = """
            Group Creation:
            .create - Create a new role for a group
            .listRole - List all available roles for a user to join
            .join - Add user to a specified role
            .leave - Remove a user from a specified role
            .delete - Delete role and its channel
            
            Task Creation(Only inside Group Channel):
            Leader Commands:
            .createTask <name> - creates task with given name
            .assignTask <@username> <task_num> - assigns numbered task to user
            .deleteTask <task_num> - deletes task
            .completeTask <task_num> - marks as complete
            All Users Commands:
            .tasks - Shows all Tasks in group
            .teamLeader - shows who the group's leader is
        """
        
        await send_embed(ctx,title,description)

async def setup(bot):
    await bot.add_cog(general_commands(bot))