
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta

class DailyTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_announcement.start() 

    @tasks.loop(hours=24)
    async def daily_announcement(self):
        for guild in self.bot.guilds:
            channels = [channel for channel in guild.channels if channel.name.startswith("standup-bot-group-")]
            for channel in channels:
                await channel.send("@everyone Standup! Put what you worked on the day before here!")

    @daily_announcement.before_loop
    async def before_daily_announcement(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = now.replace(hour=15, minute=10, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

async def setup(bot):
    await bot.add_cog(DailyTasks(bot))