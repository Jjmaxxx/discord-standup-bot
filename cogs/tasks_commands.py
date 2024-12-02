import discord
from discord.ext import commands
from config import client
from utils import send_embed
from db import execute_query, fetch_one, fetch_all


class tasks_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def valid_channel(self,ctx):
        if not ctx.channel.name.startswith("sbg-"):
            await ctx.send("This command can only be used in channels that start with 'sbg-'.")
            return False
        return True
    
    async def isUserLeader(self,ctx):
        group_name = ctx.channel.name
        user_id = ctx.author.id
        result = fetch_one('''
            SELECT COUNT(*)
            FROM groups g 
            JOIN team_leaders tl ON tl.group_id = g.id
            WHERE g.group_name = ? AND tl.user_id = ?
        ''', (group_name,user_id))[0]
        if result == 0:
            await ctx.send("You are either not authorized to modify tasks or this group does not exist in the database.")
        return result > 0
    
    async def checkRole(self, ctx):
        group_name = ctx.channel.name
        role = discord.utils.get(ctx.author.roles, name=group_name)
        if not role:
            await ctx.send("You don't have the appropriate role for this group.")
            return None
        return role
    
    async def leaderPermission(self, ctx):
        return await self.valid_channel(ctx) and await self.isUserLeader(ctx)
    
    async def showTasks(self,ctx,role):
        tasks = fetch_all("""
            SELECT * 
            FROM tasks t
            LEFT JOIN users u ON u.id = t.user_id
            WHERE t.group_id = ?;
        """, (role.id,))
        print(tasks)
        task_list = "\n".join([
            f"[{task[0]}] Task: {task[3]}, Completed: {'True' if task[5] == 1 else 'False'}, Assigned: {task[8] if task[8] else 'Unassigned'}"
            for task in tasks
        ])
        print(task_list)
        await send_embed(ctx,"Group Tasks:",task_list)

    @commands.command()
    async def createTask(self, ctx, *,task_name):
        if not await self.leaderPermission(ctx):
            return
        role = await self.checkRole(ctx)
        if not role:
            return
        execute_query('''   
            INSERT INTO tasks (group_id, task_name)
            VALUES (?, ?);
        ''', (role.id,task_name))
        await self.showTasks(ctx,role)
    
    @commands.command()
    async def assignTask(self, ctx, member: discord.Member, task_id: int):
        if not await self.leaderPermission(ctx):
            return
        
        role = await self.checkRole(ctx)
        if not role:
            return
        
        execute_query("UPDATE tasks SET user_id = ? WHERE id = ? AND group_id = ?", (member.id, task_id,role.id))

        await self.showTasks(ctx,role)

    @commands.command()
    async def deleteTask(self, ctx, task_id: int):
        if not await self.leaderPermission(ctx):
            return
        role = await self.checkRole(ctx)
        if not role:
            return
        execute_query('''
            DELETE FROM tasks WHERE id = ? AND group_id = ?;
        ''', (task_id, role.id))
        await self.showTasks(ctx,role)
    
    
    @commands.command()
    async def tasks(self, ctx):
        if not await self.valid_channel(ctx):
            return
        role = await self.checkRole(ctx)
        if not role:
            return
        await self.showTasks(ctx,role)


    @commands.command()
    async def teamLeader(self, ctx):
        if not await self.valid_channel(ctx):
            return
        role = await self.checkRole(ctx)
        if not role:
            return
        teamLeader = fetch_one("""
            SELECT u.username 
            FROM users u 
            JOIN team_leaders tl ON tl.user_id = u.id
            JOIN groups g ON tl.group_id = g.id     
            WHERE g.id = ?;         
        """, (role.id,))[0]
        await ctx.send(f"The team leader is {teamLeader}.")

    @commands.command()
    async def completeTask(self, ctx, task_id: int):
        if not await self.valid_channel(ctx):
            return
        role = await self.checkRole(ctx)
        if not role:
            return
        task = fetch_one("""
            SELECT user_id, is_completed 
            FROM tasks 
            WHERE id = ? AND group_id = ?
        """, (task_id, role.id))
        if not task:
            await ctx.send("Task not found.")
            return

        task_user_id, task_is_completed = task
        if task_is_completed == 1:
            await ctx.send("This task has already been marked as completed.")
            return
        if str(ctx.author.id) != task_user_id and not await self.isUserLeader(ctx):
            await ctx.send("You can only complete tasks assigned to you.")
            return
        
        execute_query("""
            UPDATE tasks 
            SET is_completed = 1 
            WHERE id = ? AND group_id = ?
        """, (task_id, role.id))
        await self.showTasks(ctx, role)

async def setup(bot):
    await bot.add_cog(tasks_commands(bot))