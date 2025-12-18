from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.history_keyboards import get_history_results_keyboard
from app.keyboards.main_menu import get_main_menu_keyboard
from app.services.history_service import HistoryService
from app.states.history_state import HistoryState

from app.utils.message_helpers import send_content_card, update_content_card
from app.utils.text_templates import get_history_results_message

router = Router()

@router.message(Command("history"))
@router.message(F.text == "📊 История просмотров")
async def cmd_history(message: types.Message, state: FSMContext):
    await state.clear()

    history_service = HistoryService()
    history = await history_service.get_user_history(
        telegram_id=message.from_user.id,
        limit=50,
        profile={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
        },
    )

    if not isinstance(history, list):
        await message.answer(
            "Не удалось загрузить историю. Попробуйте позже или повторите запрос.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    if not history:
        await message.answer(
            "Ваша история просмотров пуста.\n"
            "Добавьте первый просмотренный фильм или сериал!",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await state.update_data(history_records=history, history_page=0)
    await state.set_state(HistoryState.viewing)

    text = get_history_results_message(history, 0)
    keyboard = get_history_results_keyboard(history, 0)
    poster_url = (history[0].get("content") or {}).get("poster_url")

    await send_content_card(
        message, text, keyboard=keyboard, poster_url=poster_url
    )


@router.callback_query(F.data.startswith("history_page_"))
async def paginate_history(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    history = data.get("history_records", [])

    if not isinstance(history, list):
        await callback.answer("История недоступна", show_alert=True)
        return

    if not history:
        await callback.answer("История недоступна", show_alert=True)
        return

    try:
        page = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.answer("Некорректная страница", show_alert=True)
        return

    safe_page = max(0, min(page, len(history) - 1))

    text = get_history_results_message(history, safe_page)
    keyboard = get_history_results_keyboard(history, safe_page)
    poster_url = (history[safe_page].get("content") or {}).get("poster_url")

    await update_content_card(
        callback.message, text, keyboard=keyboard, poster_url=poster_url
    )
    await state.update_data(history_page=safe_page)
    await callback.answer()


@router.callback_query(F.data == "history_page_current")
async def history_page_current(callback: types.CallbackQuery):
    await callback.answer()


