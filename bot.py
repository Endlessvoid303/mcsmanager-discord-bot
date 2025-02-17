import json
import os

import time
from functools import lru_cache
import mcsapi
import dbapi
import discord
from discord import app_commands
from discord.app_commands import Choice
from dotenv import load_dotenv

load_dotenv()
discordBotToken = os.getenv("TOKEN")
# Discord bot setup
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

color_green = 65313
color_red = 16711680

# Configuration for MCSManager

# Replace with your Discord user ID
OWNER_ID = 1079043553327583332

class NameCache:
    def __init__(self, ttl=60):
        self.ttl = ttl
        self.cache_time = time.time()
        self.cached_data = None

    def get_data(self):
        # Check if cache is still valid
        if time.time() - self.cache_time < self.ttl and self.cached_data is not None:
            return self.cached_data

        # Cache has expired, fetch new data
        db = dbapi.connection()
        cursor = db.cursor()
        sql = "SELECT `NAME` FROM `users`"
        cursor.execute(sql)
        self.cached_data = cursor.fetchall()
        cursor.close()
        db.close()

        self.cache_time = time.time()
        return self.cached_data

namecache = NameCache()

def owner():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == OWNER_ID
    return app_commands.check(predicate)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        # Send a friendly message instead of a generic error
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ No permission",description="You can not use this command"), ephemeral=True)


@tree.command(name="get-users",description="get all users")
@owner()
async def get_users(interaction: discord.Interaction):
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "SELECT * from `users`"
    cursor.execute(sql)
    description = "name - discord - permission"
    users = cursor.fetchall()
    for user in users:
        description += F"\n{user[2]} - <@{user[1]}> - {user[3]}"
    # noinspection PyUnresolvedReferences
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ success",description=description),ephemeral=True)

# Slash command to add an instance mapping
@tree.command(name="add-instance", description="Add an instance mapping")
@owner()
async def add_instance(interaction: discord.Interaction, instance: str, instance_id: str, port: str):

    instance_mapping[instance] = {"id": instance_id, "port": port}
    save_instance_mappings()
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ Server added", description=f"Instance '{instance}' has been mapped to ID '{instance_id}' and port '{port}'."), ephemeral=True)

# Slash command to start an instance by its name
@tree.command(name="start", description="Start an instance by its name")
async def start(interaction: discord.Interaction, instance: str):
    instance = instance_mapping.get(instance)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ Server not found", description=f"Server '{instance}' not found. Use /add_instance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ Server starting", description=f"Attempting to start '{instance}'"))
    instance_id = instance["id"]
    response = mcsapi.start_instance(instance_id)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green, title="✅ Server starting", description=f"'{instance}' is starting"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red, title="❌ Server did not start", description=f"Failed to start '{instance}'. Error: {response['data']}"))

# Slash command to stop an instance by its name
@tree.command(name="stop", description="Stop an instance by its name")
@owner()
async def stop(interaction: discord.Interaction, instance: str):
    instance = instance_mapping.get(instance)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ Server not found", description=f"Server '{instance}' not found. Use /add_instance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="🛑 Server stopping", description=f"Attempting to stop '{instance}'"))
    instance_id = instance["id"]
    response = mcsapi.stop_instance(instance_id)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green, title="🛑 Server stopping", description=f"'{instance}' is stopping"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red, title="❌ Server did not stop", description=f"Failed to stop '{instance}'. Error: {response['data']}"))

# Slash command to restart an instance by its name
@tree.command(name="restart", description="Stop an instance by its name")
@owner()
async def restart(interaction: discord.Interaction, instance: str):

    instance = instance_mapping.get(instance)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ Server not found", description=f"Server '{instance}' not found. Use /add_instance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="🔄️ Server restarting", description=f"Attempting to restart '{instance}'"))
    instance_id = instance["id"]
    response = mcsapi.restart_instance(instance_id)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green, title="🔄️ Server restarting", description=f"'{instance}' is restarting"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red, title="❌ Server did not restart", description=f"Failed to restart '{instance}'. Error: {response['data']}"))

@tree.command(name="connect-user")
@owner()
async def connect_user(interaction: discord.Interaction, user: str, uuid: str):
    discorduuid = int(user)
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "UPDATE `users` SET DISCORDUUID = %s WHERE UUID = %s"
    arguments = [discorduuid,uuid]
    cursor.execute(sql,arguments)
    db.commit()
    cursor.close()
    db.close()
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ discord account connected", description=f"<@{discorduuid}> connected to {uuid}"), ephemeral=True)

@tree.command(name="disconnect-user")
@owner()
async def disconnect_user(interaction: discord.Interaction, user: str):
    discorduuid = int(user)
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "UPDATE `users` SET DISCORDUUID = NULL WHERE DISCORDUUID = %s"
    arguments = [discorduuid]
    cursor.execute(sql,arguments)
    db.commit()
    cursor.close()
    db.close()
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ discord account disconnected", description=f"<@{discorduuid}> disconnected"), ephemeral=True)

# Slash command to get the IP and port of an instance
@tree.command(name="ip", description="Get the IP and port of an instance")
async def ip(interaction: discord.Interaction, instance: str):
    instance = instance_mapping.get(instance)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ Server not found", description=f"Server '{instance}' not found. Use /add_instance to map it first."))
        return

    try:
        port = instance["port"]
        await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ Server ip",description=f"verweij.site:{port}"))
    except Exception as e:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server ip not found",description=f"Failed to get instance IP: {str(e)}"))

# Slash command to remove an instance by its ID
@tree.command(name="remove_instance", description="Remove an instance mapping by its name")
@owner()
async def remove_instance(interaction: discord.Interaction, instance: str):
    del instance_mapping[instance]
    await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ Server removed", description=f"Instance with name '{instance}' has been removed."))

@tree.command(name="delete-user",description="delete a user")
@owner()
async def delete_user(interaction: discord.Interaction,name:str):
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "SELECT `UUID` FROM `users` WHERE `NAME` = %s"
    params = [name]
    cursor.execute(sql,params)
    found = cursor.fetchall()
    if len(found) == 1:
        mcsapi.delete_user(found[0][0])
        sql = "DELETE FROM `users` WHERE `NAME` = %s"
        params = [name]
        cursor.execute(sql, params)
        db.commit()
        await interaction.response.send_message(embed=discord.Embed(color=color_green, title="✅ user deleted",description=f"deleted user {name} "),ephemeral=True)
    else:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ user not found",description=f"user does {name} not exist"),ephemeral=True)
    cursor.close()
    db.close()

@app_commands.describe(
    password="Password Required, 9 to 36 characters, must include uppercase and lowercase letters, and numbers"
)
@tree.command(name="add-user",description="add a user")
@owner()
async def add_user(interaction: discord.Interaction, user:str, name:str,password:str):
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "SELECT `UUID` FROM `users` WHERE NAME = %s"
    params = [name]
    cursor.execute(sql, params)
    found = cursor.fetchall()
    if len(found) == 1:
        await interaction.response.send_message(embed=discord.Embed(color=color_red, title="❌ user not created",description=f"User already exists"),ephemeral=True)
        return
    response = mcsapi.add_user(name,password,1)
    if response["status"] == 200:
        sql = "INSERT INTO `users` (UUID,DISCORDUUID,NAME,PERMS) VALUES (%s,%s,%s,%s)"
        params = [response["data"]["uuid"],int(user), name, 1]
        cursor.execute(sql, params)
        db.commit()
        cursor.close()
        db.close()
        await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ user added",description=f"created user {name} with password {password}"), ephemeral=True)
    else:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ user not created",description=f"Failed to create user: {str(response)}"), ephemeral=True)


@connect_user.autocomplete("uuid")
async def uuid_autocomplete(interaction, current):
    db = dbapi.connection()
    cursor = db.cursor()
    sql = "SELECT `UUID` FROM `users`"
    cursor.execute(sql)
    results = cursor.fetchall()
    suggestions = []
    for result in results:
        if current.lower() in result[0].lower() and len(suggestions) < 25:
            suggestions.append(Choice(value=result[0],name=result[0]))
    return suggestions

@delete_user.autocomplete("name")
async def name_autocomplete(interaction,current):
    # Filter users by their display name or username based on the current input
    suggestions = []
    names = namecache.get_data()
    for name in names:
        if current.lower() in name[0].lower() and len(suggestions) < 25:
            suggestions.append(Choice(name=name[0], value=name[0]))
    # Discord allows a maximum of 25 autocomplete suggestions
    return suggestions

@add_user.autocomplete("user")
@disconnect_user.autocomplete("user")
@connect_user.autocomplete("user")
async def user_autocomplete(interaction, current):
    # Ensure the command is run in a server (guild) context
    if not interaction.guild:
        return []

    # Get all members in the guild
    users = interaction.guild.members

    # Filter users by their display name or username based on the current input
    suggestions = []
    for user in users:
        if current.lower() in user.display_name.lower() and len(suggestions) < 25:
            suggestions.append(Choice(name=user.display_name,value=str(user.id)))
    # Discord allows a maximum of 25 autocomplete suggestions
    return suggestions

@start.autocomplete("instance")
@stop.autocomplete("instance")
@restart.autocomplete("instance")
@ip.autocomplete("instance")
@remove_instance.autocomplete("instance")
async def autocomplete_instance(interaction,current: str):
    # Suggestions based on the current input
    suggestions = []
    # Filter suggestions based on what the user is typing
    return [discord.app_commands.Choice(name=item, value=item) for item in suggestions if current.lower() in item.lower()]
dbapi.update_daemons()
dbapi.update_users()
# Run the bot
client.run(discordBotToken)  # Replace with your Discord bot token
