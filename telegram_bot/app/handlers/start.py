from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
import logging

from app.keyboards.main_menu import get_main_menu_keyboard
from app.utils.text_templates import get_start_message
from app.services.api_client import api_client

router = Router()
logger = logging.getLogger(__name__)

async def register_user_in_api(telegram_user: types.User) -> bool:
    try:
        user_data = {
            "telegram_id": str(telegram_user.id),
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
        }
        
        logger.info(f"Регистрируем пользователя: {user_data}")
        response = await api_client.post("/api/v1/users/", data=user_data) 
        if response:
            logger.info(f"Пользователь зарегистрирован: {response.get('id')}")
            return True
        else:
            check_response = await api_client.get(f"/api/v1/users/telegram/{telegram_user.id}")
            if check_response:
                logger.info(f"Пользователь уже существует: {telegram_user.id}")
                return True
            else:
                logger.error(f"Не удалось зарегистрировать пользователя {telegram_user.id}")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        return False

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    registration_success = await register_user_in_api(message.from_user)
    first_name = message.from_user.first_name
    username = message.from_user.username

    if first_name:
        name = first_name
    elif username:
        name = username
    else:
        name = "пользователь"

    text = get_start_message(name)

    if not registration_success:
        text += "\n\n <i>Возникли проблемы с регистрацией. Некоторые функции могут быть недоступны.</i>"
    else:
        text += "\n\n<i>Регистрация успешна! Все функции доступны.</i>"

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )
