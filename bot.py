import json
import os
import time

from functools import lru_cache
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.app_commands import Choice

import discord_commands
import dbapi

color_green = 65313
color_red = 16711680
OWNER_ID = 1079043553327583332

load_dotenv()
discordBotToken = os.getenv("TOKEN")
# Discord bot setup
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
discord_commands.load_commands(tree)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

dbapi.update_daemons()
dbapi.update_users()
# Run the bot
client.run(discordBotToken)  # Replace with your Discord bot token
