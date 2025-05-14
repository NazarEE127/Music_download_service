import os
import sqlite3

DB_PATH = os.path.join("db\\base.db")
base = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = base.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS users_tg (
        id_user INTEGER PRIMARY KEY,
        name TEXT
    )
""")

base.commit()
