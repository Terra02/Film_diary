from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_watchlist_results_keyboard(results: list, current_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not results:
        builder.button(text="🏠 Меню", callback_data="return_to_menu")
        builder.adjust(1)
        return builder.as_markup()

    safe_page = max(0, min(current_page, len(results) - 1))

    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить в просмотренное",
            callback_data=f"watchlist_add_{safe_page}",
        ),
        InlineKeyboardButton(
            text="🗑️ Очистить",
            callback_data="watchlist_clear",
        ),
        InlineKeyboardButton(text="🏠 Меню", callback_data="return_to_menu"),
    )

    navigation_buttons = []
    if safe_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"watchlist_page_{safe_page-1}"
            )
        )
    if safe_page < len(results) - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"watchlist_page_{safe_page+1}"
            )
        )

    if navigation_buttons:
        builder.row(*navigation_buttons)

    return builder.as_markup()
