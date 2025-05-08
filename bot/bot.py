import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import main_handler
from preload.config import *
from db.db_adapter.databases import *
import logging
from preload.functions import *

logging.basicConfig(level=logging.INFO, filename="logs\\handlers.log", filemode="w",
                    encoding="utf-8")


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_routers(main_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        print("Бот запустился!")
        asyncio.run(main())
    except KeyboardInterrupt:
        base.commit()
        base.close()

