import discord


async def send_embed(channel,title,description, color=discord.Color.blurple()):
    embed = discord.Embed(
        color = color,
        title = title,
        description = description
    )
    embed.set_thumbnail(url = "https://seeklogo.com/images/S/san-jose-state-spartans-logo-E3E560A879-seeklogo.com.png")
    await channel.send(embed = embed)
