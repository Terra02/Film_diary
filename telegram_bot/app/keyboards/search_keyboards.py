from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

__all__ = ["get_search_results_keyboard"]


def get_search_results_keyboard(results: list, current_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not results:
        builder.button(text="🔍 Новый поиск", callback_data="new_search")
        builder.button(text="🏠 Меню", callback_data="return_to_menu")
        builder.adjust(1)
        return builder.as_markup()

    safe_page = max(0, min(current_page, len(results) - 1))

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить в просмотренное",
            callback_data=f"search_add_{safe_page}",
        ),
        InlineKeyboardButton(
            text="📝 Добавить в watchlist",
            callback_data=f"search_watchlist_{safe_page}",
        ),
    )

    navigation_buttons = []
    if safe_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_page_{safe_page-1}")
        )
    if safe_page < len(results) - 1:
        navigation_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_page_{safe_page+1}")
        )

    if navigation_buttons:
        builder.row(*navigation_buttons)

    builder.row(
        InlineKeyboardButton(text="🔍 Новый поиск", callback_data="new_search"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="return_to_menu"),
    )

    return builder.as_markup()
