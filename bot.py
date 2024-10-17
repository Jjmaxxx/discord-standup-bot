import discord
import asyncio
import config
import os
from discord.ext import commands
from cogwatch import Watcher

# Set up the bot with a command prefix
bot = commands.Bot(command_prefix='#', intents=config.intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    #this is just so if you change a command in the cogs folder it will automatically reload it
    watcher = Watcher(bot, path='cogs', preload=True, debug=False)
    await watcher.start()

async def load():
    #load py files in cogs folder
    for filename in os.listdir("./cogs"):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load()
    # Run the bot
    await bot.start(config.TOKEN)

#asyncio.run just allows you to run async functions in python
asyncio.run(main())