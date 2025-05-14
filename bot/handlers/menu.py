from aiogram import Router, Bot, F
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
from preload.states import *
from preload.keyboard import *
from aiogram.types import FSInputFile


router = Router()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
user_adapter = UsersAdapter()


@router.message(Command(commands=['stop']))
async def stop_func(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)


@router.callback_query(F.data == "download_track")
async def download_track(callback: CallbackQuery, state: FSMContext):
    await state.set_state(uForm.download_track)
    await callback.message.answer("Введите песню, которую хотите скачать\n"
                                  "Формат ввода: <b>Исполнитель - Название</b>\n"
                                  "Чтобы остановить, напишите /stop")


@router.message(uForm.download_track, F.text)
async def download_track_api(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)
        return

    await state.clear()
    search_msg = await message.answer("Идёт скачивание...")
    
    try:
        req = f"http://127.0.0.1:5000/api/v1/track/{message.text}"
        response = requests.get(req)
        
        if response.status_code != 200:
            await search_msg.delete()
            await message.answer("Не удалось найти трек.", reply_markup=kb_stop)
            return
            
        data = response.json()
        
        if data.get("response") != "OK":
            await search_msg.delete()
            await message.answer("Не удалось найти трек.", reply_markup=kb_stop)
            return
            
        filename = os.path.basename(data.get("filename", ""))
        if not filename:
            await search_msg.delete()
            await message.answer("Не удалось получить файл трека.", reply_markup=kb_stop)
            return
            
        file_path = os.path.join('..', 'temp', filename)
        abs_file_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_file_path):
            await search_msg.delete()
            await message.answer("Файл трека не найден.", reply_markup=kb_stop)
            return
            
        try:
            audio_file = FSInputFile(abs_file_path)

            try:
                await search_msg.delete()
            except Exception:
                pass
                
            await message.answer_audio(
                audio=audio_file,
                reply_markup=kb_stop
            )

            # audio_file.close()
            os.remove(abs_file_path)
            
        except Exception as e:
            print(f"Ошибка при отправке файла: {e}")
            await message.answer("Произошла ошибка при отправке трека.", reply_markup=kb_stop)
            
    except Exception as e:
        print(f"Ошибка при скачивании трека: {e}")
        try:
            await search_msg.delete()
        except Exception:
            pass
        await message.answer("Произошла ошибка при скачивании трека.", reply_markup=kb_stop)


@router.callback_query(F.data == "find_album")
async def find_album(callback: CallbackQuery, state: FSMContext):
    await state.set_state(uForm.find_album)
    await callback.message.answer("Введите альбом, который хотите найти\n"
                                  "Формат ввода: <b>Исполнитель - Название</b>\n"
                                  "Чтобы остановить, напишите /stop")


@router.message(uForm.find_album, F.text)
async def find_album_api(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)
        return

    await state.clear()
    search_msg = await message.answer("Идёт поиск альбома...")
    req = f"http://127.0.0.1:5000/api/v1/album/{message.text}"
    response = requests.get(req).json()
    
    if response.get("response") != "OK":
        await search_msg.delete()
        await message.answer("Не удалось найти альбом.", reply_markup=kb_stop)
        return
        
    album_info = response.get("album_info", {})
    tracks = album_info.get("tracks", [])

    album_text = f"🎵 <b>{album_info.get('title', '')}</b>\n"
    album_text += f"👤 <b>{', '.join(album_info.get('artists', []))}</b>\n"
    album_text += f"📅 {album_info.get('year', '')}\n"
    album_text += f"🎼 {album_info.get('genre', '')}\n\n"
    album_text += "📋 <b>Треки:</b>\n"
    
    for i, track in enumerate(tracks, 1):
        artists = ', '.join(track.get('artists', []))
        album_text += f"{i}. <b>{track.get('title', '')}</b>\n"
        album_text += f"   👤 {artists}\n"
        album_text += f"   ⏱ {track.get('duration', '')}\n"
        album_text += f"   🔗 <a href='https://music.yandex.ru/track/{track.get('id')}'>Ссылка на трек</a>\n\n"
    
    await search_msg.delete()
    if album_info.get('cover'):
        await message.answer_photo(album_info.get('cover'))
    await message.answer(album_text, reply_markup=kb_stop, parse_mode="HTML")


@router.callback_query(F.data == "ai_tracks")
async def ai_tracks(callback: CallbackQuery, state: FSMContext):
    await state.set_state(uForm.ai_tracks)
    await callback.message.answer("Введите несколько треков, которые вам нравятся(минимум 3) "
                                  "и ИИ подберёт вам рекомендации\n"
                                  "Формат ввода: <b>Исполнитель - Название</b>\n"
                                  "              <b>Исполнитель - Название</b>\n"
                                  "              <b>Исполнитель - Название</b>\n"
                                  "                                       и тд...\n"
                                  "Чтобы остановить, напишите /stop")


@router.message(uForm.ai_tracks, F.text)
async def ai_tracks_api(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)
        return

    await state.clear()
    search_msg = await message.answer("Идёт поиск рекомендаций...")
    req = f"http://127.0.0.1:5000/api/v1/AI_tracks/{message.text}"
    response = requests.get(req).json()
    
    if response.get("response") != "OK":
        await search_msg.delete()
        await message.answer("Не удалось найти рекомендации.", reply_markup=kb_stop)
        return
        
    recommendations = response.get("recommendations", [])

    result = "🎵 <b>Рекомендуемые треки:</b>\n\n"
    
    for i, track in enumerate(recommendations, 1):
        result += f"{i}. <b>{track.get('title', '')}</b>\n"
        result += f"   👤 {', '.join(track.get('artists', []))}\n"
        result += f"   ⏱ {track.get('duration', '')}\n"
        if track.get('cover'):
            result += f"   🖼 <a href='{track.get('cover')}'>Обложка</a>\n"
        result += f"   🔗 <a href='{track.get('link')}'>Ссылка на трек</a>\n\n"
    
    await search_msg.delete()
    await message.answer(result, reply_markup=kb_stop, parse_mode="HTML")


@router.callback_query(F.data == "similar_tracks")
async def similar_tracks(callback: CallbackQuery, state: FSMContext):
    await state.set_state(uForm.similar_tracks)
    await callback.message.answer("Введите альбом, который хотите найти\n"
                                  "Формат ввода: <b>Исполнитель - Название</b>\n"
                                  "Чтобы остановить, напишите /stop")


@router.message(uForm.similar_tracks, F.text)
async def similar_tracks_api(message: Message, state: FSMContext):
    if message.text == "/stop":
        await state.clear()
        await message.answer('<b>🔊Меню🔊</b>', reply_markup=menu_kb)
        return

    await state.clear()
    search_msg = await message.answer("Идёт поиск похожих треков...")
    req = f"http://127.0.0.1:5000/api/v1/similar/{message.text}"
    response = requests.get(req).json()
    
    if response.get("response") != "OK":
        await search_msg.delete()
        await message.answer("Не удалось найти похожие треки.", reply_markup=kb_stop)
        return
        
    original_track = response.get("original_track", {})
    similar_tracks = response.get("similar_tracks", [])

    result = "🎵 <b>Оригинальный трек:</b>\n"
    result += f"<b>{original_track.get('title', '')}</b>\n"
    result += f"👤 {', '.join(original_track.get('artists', []))}\n"
    result += f"⏱ {original_track.get('duration', '')}\n"
    if original_track.get('cover'):
        result += f"🖼 <a href='{original_track.get('cover')}'>Обложка</a>\n"
    result += f"🔗 <a href='{original_track.get('link')}'>Ссылка на трек</a>\n\n"

    result += "🎵 <b>Похожие треки:</b>\n\n"
    
    for i, track in enumerate(similar_tracks, 1):
        result += f"{i}. <b>{track.get('title', '')}</b>\n"
        result += f"   👤 {', '.join(track.get('artists', []))}\n"
        result += f"   ⏱ {track.get('duration', '')}\n"
        if track.get('cover'):
            result += f"   🖼 <a href='{track.get('cover')}'>Обложка</a>\n"
        result += f"   🔗 <a href='{track.get('link')}'>Ссылка на трек</a>\n\n"
    
    await search_msg.delete()
    await message.answer(result, reply_markup=kb_stop, parse_mode="HTML")
