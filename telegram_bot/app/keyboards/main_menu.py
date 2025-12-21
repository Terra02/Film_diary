from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="📊 История просмотров"),
            KeyboardButton(text="📋 Список желаемого")
        ],
        [
            KeyboardButton(text="🔍 Поиск"),
            KeyboardButton(text="📈 Аналитика")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

