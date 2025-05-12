from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import requests
import os

from bot.preload.config import TOKEN
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

API_URL_SIMILAR = "http://localhost:5000/api/v1/similar/"
API_URL_TRACK = "http://localhost:5000/api/v1/track/"

@router.message(Command(commands=['start']))
async def start_func(message: Message, state: FSMContext):
    await message.answer("Привет! Введи название трека.")

@router.message()
async def search_tracks(message: Message):
    user_input = message.text.strip()
    if not user_input:
        await message.answer("Пожалуйста, введите название трека.")
        return

    search_msg = await message.answer("Ищу похожие треки...")

    try:
        response = requests.get(API_URL_SIMILAR + user_input)
        if response.status_code != 200:
            await search_msg.delete()
            await message.answer("Произошла ошибка при поиске трека.")
            return

        data = response.json()
        if "error" in data or not data.get("similar_tracks"):
            await search_msg.delete()
            await message.answer("Я не смог найти подходящий трек.")
            return

        tracks = data["similar_tracks"]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{track['title']} - {', '.join(track['artists'])}",
                        callback_data=f"track_{track['id']}"
                    )
                ]
                for track in tracks
            ]
        )

        await search_msg.delete()
        await message.answer("Выбери трек из предложенных вариантов:", reply_markup=keyboard)

    except Exception as e:
        await search_msg.delete()
        await message.answer("Произошла ошибка при поиске трека.")

@router.callback_query(lambda c: c.data and c.data.startswith("track_"))
async def handle_track_selection(callback: CallbackQuery):
    await callback.message.delete()
    track_id = callback.data[len("track_"):]
    api_url = f"http://localhost:5000/api/v1/track/{track_id}?bot=1"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        filename = data.get("filename")
        if filename and os.path.exists(filename):
            with open(filename, "rb") as audio:
                await callback.message.answer_audio(audio)
            os.remove(filename)
        else:
            await callback.message.answer("Не удалось найти файл трека.")
    else:
        await callback.message.answer("Не удалось скачать трек.")
    await callback.answer()
