import discord
from discord import app_commands
import json

# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

color_green = 65313
color_red = 16711680

# Configuration for MCSManager
import requests

def getrequest(location:str,params:dict = {}):
    # Define the API URL and parameters
    url = "http://verweij.site:23333" + location
    api_key = "1a09d7a8a0b141aba376be08cccc38f2"

    # Set up headers
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    # Add the API key as a query parameter
    params["apikey"] = api_key
    try:
        # Send GET request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Print response
        #print("Response Status Code:", response.status_code)
        #print("Response Body:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error during the request:", e)
    result = response.json()
    return result

def start_instance(id:str):
    return getrequest("/api/protected_instance/open",{"uuid":id,"daemonId":"301318d9a9c340a583082c72d73690f3"})
def stop_instance(id:str):
    return getrequest("/api/protected_instance/stop",{"uuid":id,"daemonId":"301318d9a9c340a583082c72d73690f3"})
def restart_instance(id:str):
    return getrequest("/api/protected_instance/restart",{"uuid":id,"daemonId":"301318d9a9c340a583082c72d73690f3"})

# Replace with your Discord user ID
OWNER_ID = 1079043553327583332

# Local dictionary to store instance name-to-ID mappings
instance_mapping = {}

# Load instance mappings from file
def load_instance_mappings():
    global instance_mapping
    try:
        with open("ids.txt", "r") as file:
            instance_mapping = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        instance_mapping = {}

# Save instance mappings to file
def save_instance_mappings():
    with open("ids.txt", "w") as file:
        json.dump(instance_mapping, file, indent=4)

# Initialize the MCSManagerAPI

@client.event
async def on_ready():
    load_instance_mappings()
    await tree.sync()
    print(f"Logged in as {client.user}")

async def autocomplete_instancename(interaction: discord.Interaction, current: str):
    # Suggestions based on the current input
    suggestions = instance_mapping.keys()
    # Filter suggestions based on what the user is typing
    return [discord.app_commands.Choice(name=item, value=item) for item in suggestions if current.lower() in item.lower()]

# Slash command to add an instance mapping
@tree.command(name="addinstance", description="Add an instance mapping")
async def addinstance(interaction: discord.Interaction, instancename: str, instanceid: str, port: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ No permission",description="You can not use this command"), ephemeral=True)
        return

    instance_mapping[instancename] = {"id": instanceid, "port": port}
    save_instance_mappings()
    await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ Server added",description=f"Instance '{instancename}' has been mapped to ID '{instanceid}' and port '{port}'."),ephemeral=True)

# Slash command to start an instance by its name
@tree.command(name="start", description="Start an instance by its name")
async def start(interaction: discord.Interaction, instancename: str):
    instance = instance_mapping.get(instancename)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server not found",description=f"Server '{instancename}' not found. Use /addinstance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ Server starting",description=f"Attempting to start '{instancename}'"))
    instanceid = instance["id"]
    response = start_instance(instanceid)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green,title="✅ Server starting",description=f"'{instancename}' is starting"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red,title="❌ Server did not start",description=f"Failed to start '{instancename}'. Error: {response['data']}"))

@start.autocomplete("instancename")
async def start_autocomplete(interaction: discord.Interaction, current: str):
    return await autocomplete_instancename(interaction, current)

# Slash command to stop an instance by its name
@tree.command(name="stop", description="Stop an instance by its name")
async def stop(interaction: discord.Interaction, instancename: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ No permission",description="You can not use this command"), ephemeral=True)
        return

    instance = instance_mapping.get(instancename)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server not found",description=f"Server '{instancename}' not found. Use /addinstance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green,title="🛑 Server stopping",description=f"Attempting to stop '{instancename}'"))
    instanceid = instance["id"]
    response = stop_instance(instanceid)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green,title="🛑 Server stopping",description=f"'{instancename}' is stopping"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red,title="❌ Server did not stop",description=f"Failed to stop '{instancename}'. Error: {response['data']}"))

@stop.autocomplete("instancename")
async def stop_autocomplete(interaction: discord.Interaction, current: str):
    return await autocomplete_instancename(interaction, current)

# Slash command to restart an instance by its name
@tree.command(name="restart", description="Stop an instance by its name")
async def restart(interaction: discord.Interaction, instancename: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ No permission",description="You can not use this command"), ephemeral=True)
        return

    instance = instance_mapping.get(instancename)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server not found",description=f"Server '{instancename}' not found. Use /addinstance to map it first."))
        return
    await interaction.response.send_message(embed=discord.Embed(color=color_green,title="🔄️ Server restarting",description=f"Attempting to restart '{instancename}'"))
    instanceid = instance["id"]
    response = restart_instance(instanceid)

    if response["status"] == 200:
        await interaction.edit_original_response(embed=discord.Embed(color=color_green,title="🔄️ Server restarting",description=f"'{instancename}' is restarting"))
    else:
        print(response)
        await interaction.edit_original_response(embed=discord.Embed(color=color_red,title="❌ Server did not restart",description=f"Failed to restart '{instancename}'. Error: {response['data']}"))

@restart.autocomplete("instancename")
async def restart_autocomplete(interaction: discord.Interaction, current: str):
    return await autocomplete_instancename(interaction, current)

# Slash command to get the IP and port of an instance
@tree.command(name="ip", description="Get the IP and port of an instance")
async def ip(interaction: discord.Interaction, instancename: str):
    instance = instance_mapping.get(instancename)

    if not instance:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server not found",description=f"Server '{instancename}' not found. Use /addinstance to map it first."))
        return

    instanceid = instance["id"]
    try:
        port = instance["port"]
        await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ Server ip",description=f"verweij.site:{port}"))
    except Exception as e:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ Server ip not found",description=f"Failed to get instance IP: {str(e)}"))

@ip.autocomplete("instancename")
async def ip_autocomplete(interaction: discord.Interaction, current: str):
    return await autocomplete_instancename(interaction, current)

# Slash command to remove an instance by its ID
@tree.command(name="removeinstance", description="Remove an instance mapping by its name")
async def removeinstance(interaction: discord.Interaction, instancename: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(embed=discord.Embed(color=color_red,title="❌ No permission",description="You can not use this command"), ephemeral=True)
        return
    del instance_mapping[instancename]
    await interaction.response.send_message(embed=discord.Embed(color=color_green,title="✅ Server removed",description=f"Instance with name '{instancename}' has been removed."))

@removeinstance.autocomplete("instancename")
async def removeinstance_autocomplete(interaction: discord.Interaction, current: str):
    return await autocomplete_instancename(interaction, current)

# Run the bot
client.run("MTMyNTc1NTE0MzI3NDEwNjk1MA.GcH9cR.a1vqF9iGXWpCCLTSqh4KGWS9ZHhtgGzPByyg9o")  # Replace with your Discord bot token
