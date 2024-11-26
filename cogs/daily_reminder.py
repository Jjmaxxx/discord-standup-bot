
import discord
import config
import asyncio
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import sqlite3
from db import execute_query, fetch_all, fetch_one

class daily_reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_announcement.start() 
        self.daily_checkIn.start() 


    @tasks.loop(hours = 24)
    async def daily_announcement(self):
        start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        for guild in self.bot.guilds:
            channels = [channel for channel in guild.channels if channel.name.startswith(config.GROUP_PREFIX)]
            for channel in channels:
                print(channel.name)
                
                group_row = fetch_one("SELECT id FROM groups WHERE group_name = ?", (channel.name,))
                if not group_row:
                    print(f"No group_id found for channel {channel.name}")
                    continue
                group_id = group_row[0]
                responses = fetch_all('''
                    SELECT u.username, q.question_text, response_text 
                    FROM responses r
                    JOIN users u ON u.id = r.user_id
                    JOIN questions q ON q.id = r.question_id
                    WHERE group_id = ? AND joined_at BETWEEN ? AND ?
                    ORDER BY u.username, q.question_text;
                ''', (group_id, start_of_day, end_of_day))
                print(responses)
                if not responses:
                    await channel.send("No responses submitted today. Don't forget to participate!")
                    continue

                message_lines = ["**Standup Summary for Today:**\n"]
                for response in responses:
                    message_lines.append(response)

                await channel.send(message_lines)

    @daily_announcement.before_loop
    async def before_daily_announcement(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = now.replace(hour=15, minute=27, second=30, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

    @tasks.loop(hours = 24)
    async def daily_checkIn(self):
        #roles = []
        questions = fetch_all("""
            SELECT * FROM questions;
        """)

        for guild in self.bot.guilds:
            roles = [role for role in guild.roles if role.name.startswith(config.GROUP_PREFIX)]
            for role in roles:
                tasks = []
                
                for member in role.members:
                    tasks.append(self.handle_member_questions(member, role.id, questions))
                    print(role.id)
                    print(member)
                await asyncio.gather(*tasks)
    async def handle_member_questions(self, member,group_id,questions):
        try:
            for question_id, question_text in questions:
                await member.send(question_text)
                def check(message):
                        return message.author == member and isinstance(message.channel, discord.DMChannel)
                response = await self.bot.wait_for('message', check=check, timeout=3000)
                execute_query('''
                    INSERT INTO responses (user_id, group_id, question_id, response_text)
                    VALUES (?, ?, ?, ?);
                ''', (member.id, group_id, question_id, response.content))
            endResponse = "Thank You!"
            await member.send(endResponse)  
        except asyncio.TimeoutError:
            await member.send("You didn't respond in time. Moving on to the next question.")
        except Exception as e:
            print(f"Error while handling {member.name}: {e}")             

    @daily_checkIn.before_loop
    async def before_daily_checkIn(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = now.replace(hour=15, minute=26, second=30, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

async def setup(bot):
    await bot.add_cog(daily_reminder(bot))