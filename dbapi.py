from mysql.connector.abstracts import MySQLConnectionAbstract, MySQLCursorAbstract
from mysql.connector.pooling import PooledMySQLConnection
import mcsapi
import mysql.connector
from dotenv import load_dotenv
import os
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
    return  db,cursor

def update_daemons():
    db,cursor = dbapi.connection()
    daemons = mcsapi.get_daemon_data()["data"]["remote"]
    for daemon in daemons:
        uuid = daemon['uuid']
        ip = daemon['ip']
        if ip == "localhost": ip = "verweij.site"
        sql = "SELECT * FROM `daemons` WHERE UUID = %s"
        params = [uuid]
        cursor.execute(sql,params)
        found = cursor.fetchall()
        if len(found) == 1:
            sql = "UPDATE `daemons` SET IP = %s WHERE UUID = %s"
            params = [ip,uuid]
            cursor.execute(sql,params)
        else:
            sql = "INSERT INTO `daemons` (UUID,IP) VALUES (%s,%s)"
            params = [uuid,ip]
            cursor.execute(sql,params)
    db.commit()

def update_users():
    db,cursor = dbapi.connection()
    users = mcsapi.get_users(1,100)["data"]["data"]
    for user in users:
        uuid = user['uuid']
        name = user['userName']
        perms = user['permission']
        sql = "SELECT `UUID` FROM `users` WHERE UUID = %s"
        params = [uuid]
        cursor.execute(sql, params)
        found = cursor.fetchall()
        if len(found) == 1:
            sql = "UPDATE `users` SET PERMS = %s WHERE UUID = %s"
            params = [perms, uuid]
            cursor.execute(sql, params)
        else:
            sql = "INSERT INTO `users` (UUID,NAME,PERMS) VALUES (%s,%s,%s)"
            params = [uuid, name, perms]
            cursor.execute(sql, params)
    db.commit()