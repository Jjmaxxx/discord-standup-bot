import discord
from discord.ext import commands
from config import client

class general_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # List all available commands for users to use
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            color = discord.Color.blurple(),
            title = "Here Are The Available Commands:",
            description = ".create - Create a new role for a group \n"
                        ".listRole - List all available roles for a user to join \n"
                        ".join - Add user to a specified role \n"
                        ".delete - Delete role and its channel \n"
        )
        embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")

        await ctx.send(embed = embed)
    #delete this later
    @commands.command()
    async def chatgpt(self, ctx):
        print("run")
        #system is how the ai should respond, user/content is prompt
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "What are you?"
                    }
                ]
            )
            
            message = completion.choices[0].message.content
            await ctx.send(message)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("An error occurred while processing your request.")

async def setup(bot):
    await bot.add_cog(general_commands(bot))