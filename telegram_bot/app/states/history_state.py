from aiogram.fsm.state import State, StatesGroup


class HistoryState(StatesGroup):
    viewing = State()
