from db.db_adapter.databases import *
import logging

logging.basicConfig(level=logging.INFO, filename="logs\\handlers.log", filemode="w", encoding="utf-8")


class UsersAdapter:
    def __init__(self):
        self.base = base
        self.cursor = cur

    #    Методы для таблицы users

    def user_exists(self, id) -> bool:
        with self.base:
            result = self.cursor.execute('SELECT * FROM users_tg WHERE `id_user` = ?', (id,)).fetchall()
            return bool(len(result))

    def add_user(self, id_user) -> None:
        with self.base:
            logging.info("[INFO] added user to db")
            self.cursor.execute("INSERT INTO users_tg (`id_user`) VALUES(?)", (id_user,))
            base.commit()

    def add_name(self, id, name) -> None:
        with self.base:
            self.cursor.execute("UPDATE users_tg SET `name` = ? WHERE `id_user` = ?", (name, id,))
            base.commit()

    def get_name(self, id) -> str:
        with self.base:
            result = self.cursor.execute('SELECT * FROM users_tg WHERE `id_user` = ?', (id,)).fetchall()
            return result[0][1]
