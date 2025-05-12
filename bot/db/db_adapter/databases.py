import os
import sqlite3

DB_PATH = os.path.join("bot\\db\\base.db")
base = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = base.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY,
        name TEXT
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS users_tg (
        id_user INTEGER PRIMARY KEY
    )
""")

base.commit()