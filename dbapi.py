import mcsapi
import os
from dotenv import load_dotenv
import mysql.connector as connector
from mysql.connector import errorcode

load_dotenv()
DB_USER = os.getenv("DB-USER")
DB_PASS = os.getenv("DB-PASSWORD")
DB_NAME = os.getenv("DB-DATABASE")
def connection():
    db = connector.connect(
        host=os.getenv("HOST"),
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        ssl_disabled=True
    )
    cursor = db.cursor()
    return db, cursor

def update_daemons():
    """Update daemon entries in MySQL."""
    db, cursor = connection()
    daemons = mcsapi.get_daemon_data()["data"]["remote"]

    for daemon in daemons:
        uuid = daemon['uuid']
        ip = daemon['ip']
        if ip == "localhost":
            ip = "verweij.site"

        cursor.execute("SELECT * FROM `daemons` WHERE UUID = %s", [uuid])
        found = cursor.fetchall()

        if found:
            cursor.execute("UPDATE `daemons` SET IP = %s WHERE UUID = %s", [ip, uuid])
        else:
            cursor.execute("INSERT INTO `daemons` (UUID, IP) VALUES (%s, %s)", [uuid, ip])

    db.commit()
    cursor.close()
    db.close()

def update_users():
    """Update user entries in MySQL."""
    db, cursor = connection()
    users = mcsapi.get_users(1, 100)["data"]["data"]

    for user in users:
        uuid = user['uuid']
        name = user['userName']
        perms = user['permission']

        cursor.execute("SELECT `UUID` FROM `users` WHERE UUID = %s", [uuid])
        found = cursor.fetchall()

        if found:
            cursor.execute("UPDATE `users` SET PERMS = %s WHERE UUID = %s", [perms, uuid])
        else:
            cursor.execute("INSERT INTO `users` (UUID, NAME, PERMS) VALUES (%s, %s, %s)", [uuid, name, perms])

    db.commit()
    cursor.close()
    db.close()