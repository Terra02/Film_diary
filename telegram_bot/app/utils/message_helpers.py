from typing import Optional

from aiogram import types
from aiogram.types import InputMediaPhoto


def _safe_delete_message(message: types.Message) -> None:
    try:
        import asyncio

        asyncio.create_task(message.delete())
    except Exception:
        pass


async def send_content_card(
    message: types.Message,
    text: str,
    keyboard: Optional[types.InlineKeyboardMarkup] = None,
    poster_url: Optional[str] = None,
    parse_mode: str = "HTML",
) -> types.Message:
    if poster_url:
        try:
            return await message.answer_photo(
                poster_url,
                caption=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
            )
        except Exception:
            pass

    return await message.answer(text, reply_markup=keyboard, parse_mode=parse_mode)


async def update_content_card(
    message: types.Message,
    text: str,
    keyboard: Optional[types.InlineKeyboardMarkup] = None,
    poster_url: Optional[str] = None,
    parse_mode: str = "HTML",
) -> types.Message:
    if poster_url:
        if message.content_type != "photo":
            try:
                sent = await message.answer_photo(
                    poster_url,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode=parse_mode,
                )
                _safe_delete_message(message)
                return sent
            except Exception:
                pass
        else:
            try:
                media = InputMediaPhoto(
                    media=poster_url, caption=text, parse_mode=parse_mode
                )
                await message.edit_media(media, reply_markup=keyboard)
                return message
            except Exception:
                try:
                    await message.edit_caption(
                        text, reply_markup=keyboard, parse_mode=parse_mode
                    )
                    return message
                except Exception:
                    pass

    try:
        await message.edit_text(text, reply_markup=keyboard, parse_mode=parse_mode)
        return message
    except Exception:
        try:
            await message.edit_caption(
                text, reply_markup=keyboard, parse_mode=parse_mode
            )
            return message
        except Exception:
            return message
