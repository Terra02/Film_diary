from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.utils.formatters import format_analytics_message
from app.utils.text_templates import get_analytics_message

router = Router()

@router.message(Command("analytics"))
@router.message(F.text == "📈 Аналитика")
async def cmd_analytics(message: types.Message, state: FSMContext):
    await state.clear()

    text = get_analytics_message()
    
    await message.answer(text, parse_mode="HTML")

