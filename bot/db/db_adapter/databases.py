import sqlite3

# Base.db

base = sqlite3.connect("db\\base.db", check_same_thread=False)
cur = base.cursor()

# Таблица users
cur.execute("create table if not exists {}(id_user integer, name string"
            .format('users'))

base.commit()

# РАБОЧИЙ ФАЙЛ (файлы роутеров, bot.py)
