from aiogram.fsm.state import State, StatesGroup

class SearchState(StatesGroup):
    waiting_for_query = State()
    waiting_for_selection = State()
    waiting_for_season = State()
    waiting_for_episode = State()
    waiting_for_review = State()
    waiting_for_watched_at = State()
    waiting_for_rating = State()