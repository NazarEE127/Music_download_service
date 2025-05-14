from aiogram.fsm.state import State, StatesGroup


class uForm(StatesGroup):
    download_track = State()
    find_album = State()
    ai_tracks = State()
    similar_tracks = State()
