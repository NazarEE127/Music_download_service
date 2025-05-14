from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

menu_kb = [
    [InlineKeyboardButton(text='🔽Скачать трек', callback_data='download_track'),
     InlineKeyboardButton(text='💽Найти альбом', callback_data='find_album')],
    [InlineKeyboardButton(text='🎧Побдорка ИИ по моему вкусу', callback_data='ai_tracks'),
     InlineKeyboardButton(text='🎶Треки с таким же названием', callback_data='similar_tracks')]
]

menu_kb = InlineKeyboardMarkup(inline_keyboard=menu_kb)


button = [
        [KeyboardButton(text="/stop")]
    ]
kb_stop = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
