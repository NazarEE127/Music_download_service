from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import requests
import os
import logging
from preload.config import TOKEN
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from preload.keyboard import *
from db.db_adapter.users_database import UsersAdapter

router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
user_adapter = UsersAdapter()
API_URL_SIMILAR = "http://127.0.0.1:5000/api/v1/AI_tracks/"
API_URL_TRACK = "http://127.0.0.1:5000/api/v1/track/"


@router.message(Command(commands=['start']))
async def start_func(message: Message, state: FSMContext):
    logging.info(
        f'[INFO] {message.from_user.first_name} {message.from_user.last_name} started bot, id = {message.from_user.id}')
    await message.answer("Привет! Я YaMaBot - музыкальный помощник, и вот что я умею ⬇️")
    if user_adapter.user_exists(message.from_user.id):
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)
    else:
        user_adapter.add_user(message.from_user.id)
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)


