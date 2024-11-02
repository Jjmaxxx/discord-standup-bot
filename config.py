import os
import discord
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('bot_token')
print(f'Token: {TOKEN}')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

