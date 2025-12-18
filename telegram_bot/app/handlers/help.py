from aiogram import Router, types
from aiogram.filters import Command

from app.utils.text_templates import get_help_message

router = Router()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = get_help_message()
    await message.answer(text, parse_mode="HTML")