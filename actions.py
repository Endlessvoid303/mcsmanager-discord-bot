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

namecache = NameCache()

def get_users_info() -> str:
    db,cursor = dbapi.connection()
    sql = "SELECT * from `users`"
    cursor.execute(sql)
    display = "name - discord - permission"
    users = cursor.fetchall()
    for user in users:
        display += F"\n{user[2]} - <@{user[1]}> - {user[3]}"
    return display

#TODO: check if user exists before changing
#TODO: check if discorduuid is already set
#TODO: check if discorduuid is already used somewhere
def connect_discord_user_to_database(discorduuid:int,uuid:str):
    db, cursor = dbapi.connection()
    sql = "UPDATE `users` SET DISCORDUUID = %s WHERE UUID = %s"
    arguments = [discorduuid, uuid]
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