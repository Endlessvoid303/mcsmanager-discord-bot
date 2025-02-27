import time
import exceptions
import mcsapi
import dbapi

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

cache = NameCache()

def get_data():
    return cache.get_data()

def get_users_info() -> str:
    db,cursor = dbapi.connection()
    sql = "SELECT * from `users`"
    cursor.execute(sql)
    display = "name - discord - permission"
    users = cursor.fetchall()
    for user in users:
        display += F"\n{user[2]} - <@{user[1]}> - {user[3]}"
    return display

def connect_discord_user_to_database(discord_uuid:int, name:str):
    db, cursor = dbapi.connection()
    cursor.execute("SELECT NAME FROM users WHERE DISCORDUUID = %s", (discord_uuid,))
    result = cursor.fetchone()
    if result:
        raise exceptions.DiscordUuidUsed("user can not connect to database because discord uuid is already in use",{"discord_uuid":discord_uuid,"name":name})
    cursor.execute("SELECT DISCORDUUID FROM users WHERE NAME = %s", (name,))
    result = cursor.fetchone()
    if not result:
        raise exceptions.UserMissing("user can not connect to database because user doesn't exist",{"discord_uuid":discord_uuid,"name":name})
    if result[0]:
        raise exceptions.DiscordUuidUsed("user can not connect to database because user already has a discord uuid",{"discord_uuid":discord_uuid,"name":name})
    sql = "UPDATE users SET DISCORDUUID = %s WHERE NAME = %s"
    arguments = [discord_uuid, name]
    cursor.execute(sql, arguments)
    db.commit()

#TODO: check if discorduuid is connected before disconnecting
def disconnect_discord_user_from_database(discorduuid:int):
    db, cursor = dbapi.connection()
    sql = "UPDATE `users` SET DISCORDUUID = NULL WHERE DISCORDUUID = %s"
    arguments = [discorduuid]
    cursor.execute(sql, arguments)
    db.commit()

#FIXME: the user does not get deleted from mcs
def delete_user(name:str):
    db, cursor = dbapi.connection()
    sql = "SELECT `UUID` FROM `users` WHERE `NAME` = %s"
    params = [name]
    cursor.execute(sql, params)
    found = cursor.fetchall()
    if len(found) == 1:
        mcsapi.delete_user(found[0][0])
        sql = "DELETE FROM `users` WHERE `NAME` = %s"
        params = [name]
        cursor.execute(sql, params)
        db.commit()
    elif len(found) > 1:
        raise exceptions.MultipleUsersError(F"multiple users with `{name}` name were found in database")
    elif len(found) == 0:
        raise exceptions.UserMissing(F"no user was found with `{name}` name in the database")