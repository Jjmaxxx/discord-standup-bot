
import discord
import config
import asyncio
import openai
from config import client
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
                    embed = discord.Embed(
                        color = discord.Color.blurple(),
                        title = "No Responses Submitted Today",
                        description = "Don't forget to participate!"
                    )
                    embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
                    await channel.send(embed = embed)
                    continue
                
                ai_prompt = str(responses)

                # embed = discord.Embed(
                #     color = discord.Color.blurple(),
                #     title = "**Standup Summary for Today:**"
                # )

                # Break down each response to allow for embed compatability
                # for response in responses:
                #     username = response[0]
                #     question_text = response[1]
                #     response_text = response[2]
                #     embed.add_field(name = f"{username} : {question_text}", 
                #                     value = response_text, 
                #                     inline = False)
                
                # embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
                # await channel.send(embed = embed)

                print("it gets here")
                
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages = [
                         {"role": "user", "content": f"Take this data and give suggestions for the group's next steps based on their responses but make it short and also do a short summary of what each group member has done: {ai_prompt}"}
                    ]
                )

                message = completion.choices[0].message.content

                embed = discord.Embed(
                    color = discord.Color.blurple(),
                    title = "Standup Summary for Today:",
                    description = message
                )
                embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
                await channel.send(embed = embed)

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
        #roles = [] 
        questions = fetch_all("""
            SELECT * FROM questions;
        """)
        user_tasks = {}

        for guild in self.bot.guilds:
            roles = [role for role in guild.roles if role.name.startswith(config.GROUP_PREFIX)]
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
        target_time = now.replace(hour=14, minute=46, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        await discord.utils.sleep_until(target_time)

async def setup(bot):
    await bot.add_cog(daily_reminder(bot))