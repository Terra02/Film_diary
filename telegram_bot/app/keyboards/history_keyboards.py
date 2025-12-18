from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_history_results_keyboard(records: list, current_page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not records:
        builder.button(text="🏠 Меню", callback_data="return_to_menu")
        return builder.as_markup()

    safe_page = max(0, min(current_page, len(records) - 1))

    navigation_buttons = []
    if safe_page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"history_page_{safe_page-1}")
        )
    navigation_buttons.append(
        InlineKeyboardButton(
            text=f"{safe_page + 1}/{len(records)}", callback_data="history_page_current"
        )
    )
    if safe_page < len(records) - 1:
        navigation_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=f"history_page_{safe_page+1}")
        )

    builder.row(*navigation_buttons)
    builder.row(InlineKeyboardButton(text="🏠 Меню", callback_data="return_to_menu"))

    return builder.as_markup()

