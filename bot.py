import discord
import asyncio
import config
import os
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from cogwatch import Watcher

# Set up the bot with a command prefix
bot = commands.Bot(command_prefix = '.', intents = discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_guild_join(guild):
    category_name = config.CATEGORY_NAME
    category = discord.utils.get(guild.categories, name = category_name)
    if category is None:
        category = await guild.create_category(category_name)
        print(f'Category "{category_name}" created in guild "{guild.name}".')
    else:
        print(f'Category "{category_name}" already exists in guild "{guild.name}".')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    #synced_commands = await bot.tree.sync()

    #this is just so if you change a command in the cogs folder it will automatically reload it
    watcher = Watcher(bot, path = 'cogs', preload = True, debug = False)
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