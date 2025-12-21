from aiogram.fsm.state import StatesGroup, State


class WatchlistState(StatesGroup):
    viewing = State()
    waiting_for_season = State()
    waiting_for_episode = State()
    waiting_for_review = State()
    waiting_for_watched_at = State()
    waiting_for_rating = State()
