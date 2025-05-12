import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables from .env
load_dotenv()

# Your Discord User ID for mentions
USER_ID = 1289710977926959165

# Start with Kitsune and Dragon as default tracked fruits
FRUITS_TO_TRACK = ["Kitsune", "Dragon"]

# Load Discord token and channel ID from environment
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1371312057915412480

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

async def check_stock():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    already_alerted = set()

    while not client.is_closed():
        try:
            url = "https://fruityblox.com/stock"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            stock = [fruit.text.strip() for fruit in soup.find_all('h3')]

            embed = discord.Embed(title="📊 **Current Stock Status**", color=discord.Color.blue())

            # Show all fruits, tracked fruits get emojis
            for fruit in stock:
                if fruit in FRUITS_TO_TRACK:
                    embed.add_field(name=f"✅ **{fruit}**", value="In Stock!", inline=False)
                else:
                    embed.add_field(name=f"**{fruit}**", value="In Stock", inline=False)

            # Add tracked fruits that are NOT in stock
            for fruit in FRUITS_TO_TRACK:
                if fruit not in stock:
                    embed.add_field(name=f"❌ **{fruit}**", value="Out of Stock", inline=False)

            await channel.send(embed=embed)

            # Mention you if tracked fruits are in stock
            for fruit in FRUITS_TO_TRACK:
                if fruit in stock and fruit not in already_alerted:
                    user = await client.fetch_user(USER_ID)
                    await channel.send(f"{user.mention} 🔥 **{fruit}** is now in stock!")
                    already_alerted.add(fruit)

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(300)  # Repeat every 5 minutes

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    client.loop.create_task(check_stock())

@client.event
async def on_message(message):
    await client.process_commands(message)

    if message.content.startswith("!checkstock") or message.content.startswith("!stock"):
        try:
            url = "https://fruityblox.com/stock"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            stock = [fruit.text.strip() for fruit in soup.find_all('h3')]

            embed = discord.Embed(title="📊 **Full Stock Status**", color=discord.Color.blue())

            # Show all fruits, tracked fruits get emojis
            for fruit in stock:
                if fruit in FRUITS_TO_TRACK:
                    embed.add_field(name=f"✅ **{fruit}**", value="In Stock!", inline=False)
                else:
                    embed.add_field(name=f"**{fruit}**", value="In Stock", inline=False)

            # Show tracked fruits not in stock
            for fruit in FRUITS_TO_TRACK:
                if fruit not in stock:
                    embed.add_field(name=f"❌ **{fruit}**", value="Out of Stock", inline=False)

            await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send("❌ Error checking stock.")
            print(f"Error: {e}")

@client.command()
async def addfruit(ctx, fruit_name: str):
    if fruit_name not in FRUITS_TO_TRACK:
        FRUITS_TO_TRACK.append(fruit_name)
        await ctx.send(f"✅ **{fruit_name}** has been added to the tracked list!")
    else:
        await ctx.send(f"❌ **{fruit_name}** is already being tracked.")

@client.command()
async def removefruit(ctx, fruit_name: str):
    if fruit_name in FRUITS_TO_TRACK:
        FRUITS_TO_TRACK.remove(fruit_name)
        await ctx.send(f"✅ **{fruit_name}** has been removed from the tracked list.")
    else:
        await ctx.send(f"❌ **{fruit_name}** is not in the tracked list.")

client.run(TOKEN)
