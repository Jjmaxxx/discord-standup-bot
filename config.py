import os
import discord
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('bot_token')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


GROUP_PREFIX= "sbg-"
CATEGORY_NAME = "standup-bot-groups"