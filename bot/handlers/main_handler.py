from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.preload.keyboard import *
from bot.preload.functions import *
from bot.preload.config import *
from bot.db.db_adapter.users_database import UsersAdapter
import logging
from aiogram.fsm.context import FSMContext
from bot.preload.states import *
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO, filename="logs\\handlers.log", filemode="w",
                    encoding="utf-8")

user_adapter = UsersAdapter()
router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@router.message(Command(commands=['start']))
async def start_func(message: Message, state: FSMContext):
    logging.info(
        f'[INFO] {message.from_user.first_name} {message.from_user.last_name} started bot, id = {message.from_user.id}')
    await message.answer("Привет")
