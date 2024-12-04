import discord
import config
import asyncio
import openai
from config import client
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from utils import send_embed
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

        # Cycle through all of the servers using the bot
        for guild in self.bot.guilds:
            # Cycle through all channels that have been created using the bot
            channels = [channel for channel in guild.channels if channel.name.startswith(config.GROUP_PREFIX)]
            for channel in channels:
                print(channel.name)
                # Find the group associated with the channel
                group_row = fetch_one("SELECT id FROM groups WHERE group_name = ?", (channel.name,))
                if not group_row:
                    print(f"No group_id found for channel {channel.name}")
                    continue
                group_id = group_row[0]
                # Grab the stored responses 
                responses = fetch_all('''
                    SELECT u.username, q.question_text, response_text 
                    FROM responses r
                    JOIN users u ON u.id = r.user_id
                    JOIN questions q ON q.id = r.question_id
                    WHERE group_id = ? AND joined_at BETWEEN ? AND ?
                    ORDER BY u.username, q.question_text;
                ''', (group_id, start_of_day, end_of_day))
                print(responses)
                # If there are no recorded responses, notfiy that no responses were sent
                if not responses:
                    await send_embed(channel, "No Responses Submitted Today","Don't forget to participate!")
                    continue
                
                # Turn database information into a string for AI prompting
                ai_prompt = str(responses)
                
                # Prompt Chatgpt with the responses to send to the group channel
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages = [
                        {"role": "user", "content": f"Take this data and give suggestions for the group's next steps based on their responses but make it short and do a short summary of what each group member has done: {ai_prompt}"}
                    ]
                )

                message = completion.choices[0].message.content

                await send_embed(channel,"Standup Summary for Today:",message)

    # This method will resend the daily_announcement every 24hrs at a specified time
    @daily_announcement.before_loop
    async def before_daily_announcement(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = now.replace(hour=14, minute=50, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

    @tasks.loop(hours = 24)
    async def daily_checkIn(self):
        # Grab the check-in questions from the database
        questions = fetch_all("""
            SELECT * FROM questions;
        """)
        user_tasks = {}

        # Cycle through all of the Discord servers using the bot
        for guild in self.bot.guilds:
            # Cycle through all of the roles within a given server that have been created with the bot
            roles = [role for role in guild.roles if role.name.startswith(config.GROUP_PREFIX)]
            # For each role, cycle through all of its members
            for role in roles:
                for member in role.members:
                    if member.id not in user_tasks:
                        user_tasks[member.id] = []
                    user_tasks[member.id].append((member, role, questions))
        tasks = [self.handle_user_groups(user_id, user_groups) for user_id, user_groups in user_tasks.items()]
        await asyncio.gather(*tasks)
    
    async def handle_user_groups(self,user_id, user_groups):
        #if user is part of multiple groups, send group messages individually
        for member, group, questions in user_groups:
            await self.handle_member_questions(member, group, questions)
    
    async def handle_member_questions(self, member,group,questions):
        try:
            group_id = group.id
            beginResponse = f"Hello! This is your daily checkin for the group: {group.name}."
            await member.send(beginResponse)
            # Ask each question in database to user individually unitl a response has been given
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
        # If a response has not been given within the allotted time, move to next question
        except asyncio.TimeoutError:
            await member.send("You didn't respond in time. Moving on to the next question.")
        except Exception as e:
            print(f"Error while handling {member.name}: {e}")             

    # This method will enable the bot to prompt the questions to all users on a daily basis
    @daily_checkIn.before_loop
    async def before_daily_checkIn(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        target_time = now.replace(hour=14, minute=46, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

async def setup(bot):
    await bot.add_cog(daily_reminder(bot))