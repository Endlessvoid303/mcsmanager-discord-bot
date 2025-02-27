import actions
import discord
from discord import app_commands

import exceptions


def load_commands(tree: app_commands.CommandTree):
    def owner():
        async def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == OWNER_ID

        return app_commands.check(predicate)

    @tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            # Send a friendly message instead of a generic error
            # noinspection PyUnresolvedReferences
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_red,
                    title="❌ No permission",
                    description="You can not use this command"
                ),
                ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_red,
                    title="❌ error",
                    description="something went wrong ¯\\_(ツ)_/¯"),
                ephemeral=True)

    @tree.command(name="get-users", description="get all users")
    @owner()
    async def get_users(interaction: discord.Interaction):
        display = actions.get_users_info()
        await interaction.response.send_message(
            embed=discord.Embed(
                color=color_green,
                title="✅ success",
                description=display),
            ephemeral=True)

    @tree.command(name="connect-user")
    @owner()
    async def connect_user(interaction: discord.Interaction, user: str, uuid: str):
        discorduuid = int(user)
        actions.connect_discord_user_to_database(discorduuid,uuid)
        await interaction.response.send_message(
            embed=discord.Embed(
                color=color_green,
                title="✅ discord account connected",
                description=f"<@{discorduuid}> connected to {uuid}"),
            ephemeral=True)

    @tree.command(name="disconnect-user")
    @owner()
    async def disconnect_user(interaction: discord.Interaction, user: str):
        discorduuid = int(user)
        actions.disconnect_discord_user_from_database(discorduuid)
        await interaction.response.send_message(
            embed=discord.Embed(
                color=color_green,
                title="✅ discord account disconnected",
                description=f"<@{discorduuid}> disconnected"),
            ephemeral=True)

    @tree.command(name="panel", description="open the panel")
    async def panel(interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                color=color_green,
                title="✅ panel link",
                description=f"http://verweij.site:23333/"))

    @tree.command(name="delete-user", description="delete a user")
    @owner()
    async def delete_user(interaction: discord.Interaction, name: str):
        try:
            actions.delete_user(name)
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_green,
                    title="✅ user deleted",
                    description=f"deleted user {name} "),
                ephemeral=True)
        except (exceptions.MultipleUsersError,exceptions.UserMissing) as e:
            print(F"exception caught: {e.message}")
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_red,
                    title="❌ failed user deletion",
                    description=e.generic),
                ephemeral=True)

#TODO: move function and add errors
    @app_commands.describe(
        password="Password Required, 9 to 36 characters, must include uppercase and lowercase letters, and numbers"
    )
    @tree.command(name="add-user", description="add a user")
    @owner()
    async def add_user(interaction: discord.Interaction, user: str, name: str, password: str):
        db = dbapi.connection()
        cursor = db.cursor()
        sql = "SELECT `UUID` FROM `users` WHERE NAME = %s"
        params = [name]
        cursor.execute(sql, params)
        found = cursor.fetchall()
        if len(found) == 1:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_red,
                    title="❌ user not created",
                    description=f"User already exists"),
                ephemeral=True)
            return
        response = mcsapi.add_user(name, password, 1)
        if response["status"] == 200:
            sql = "INSERT INTO `users` (UUID,DISCORDUUID,NAME,PERMS) VALUES (%s,%s,%s,%s)"
            params = [response["data"]["uuid"], int(user), name, 1]
            cursor.execute(sql, params)
            db.commit()
            cursor.close()
            db.close()
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_green,
                    title="✅ user added",
                    description=f"created user {name} with password {password}"),
                ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=color_red,
                    title="❌ user not created",
                    description=f"Failed to create user: {str(response)}"),
                ephemeral=True)



    @connect_user.autocomplete("uuid")
    async def uuid_autocomplete(interaction, current):
        db,cursor = dbapi.connection()
        sql = "SELECT `UUID` FROM `users`"
        cursor.execute(sql)
        results = cursor.fetchall()
        suggestions = []
        for result in results:
            if current.lower() in result[0].lower() and len(suggestions) < 25:
                suggestions.append(Choice(value=result[0], name=result[0]))
        return suggestions

    @delete_user.autocomplete("name")
    async def name_autocomplete(interaction, current):
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
                suggestions.append(Choice(name=user.display_name, value=str(user.id)))
        # Discord allows a maximum of 25 autocomplete suggestions
        return suggestions

    @start.autocomplete("instance")
    @stop.autocomplete("instance")
    @restart.autocomplete("instance")
    @ip.autocomplete("instance")
    @remove_instance.autocomplete("instance")
    async def autocomplete_instance(interaction, current: str):
        # Suggestions based on the current input
        suggestions = []
        # Filter suggestions based on what the user is typing
        return [discord.app_commands.Choice(name=item, value=item) for item in suggestions if
                current.lower() in item.lower()]