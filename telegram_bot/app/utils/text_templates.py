from typing import List, Dict, Any

__all__ = [
    "get_start_message",
    "get_help_message",
    "get_history_results_message",
    "get_watchlist_message",
    "get_search_results_message",
    "get_analytics_message",
    "get_settings_message",
]

def get_start_message(username: str) -> str:
    return (
        f"Добро пожаловать в Movie Tracker, {username}!\n\n"
        "Здесь вы можете:\n"
        "• Вести историю просмотров\n"
        "• Создать список желаемого\n"
        "• Искать фильмы и сериалы\n"
        "• Смотреть аналитику\n\n"
        "Выберите действие в меню ниже 👇"
    )

def get_help_message() -> str:
    return (
        "<b>Movie Tracker Bot - Помощь</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start - Начать работу\n"
        "/help - Показать эту справку\n"
        "/history - История просмотров\n"
        "/watchlist - Список желаемого\n"
        "/search - Поиск контента\n"
        "/analytics - Аналитика\n\n"
        "<b>Как использовать:</b>\n"
        "1. Добавляйте просмотренные фильмы и сериалы\n"
        "2. Оценивайте их от 1 до 10\n"
        "3. Следите за своей статистикой\n"
        "4. Планируйте будущие просмотры\n\n"
        "Для начала работы нажмите /start"
    )

def get_history_results_message(history: List[Dict[str, Any]], page: int) -> str:
    if not history:
        return "Ваша история просмотров пуста."

    index = max(0, min(page, len(history) - 1))
    record = history[index]
    content = record.get("content") or {}

    title = content.get("title") or record.get("content_title") or "Без названия"
    year = content.get("release_year") or "неизвестно"
    imdb_rating = content.get("imdb_rating")
    imdb_rating_text = f"{imdb_rating}/10" if imdb_rating not in (None, "") else "нет данных"
    genre = content.get("genre") or "нет данных"
    director = content.get("director") or "нет данных"
    cast = content.get("actors_cast") or content.get("cast") or "нет данных"
    description = content.get("description") or "Описание недоступно"

    if len(description) > 600:
        description = description[:600].rstrip() + "..."

    content_type = content.get("content_type") or "movie"
    type_text = "фильм" if content_type == "movie" else "сериал"

    user_rating = record.get("rating")
    user_rating_text = f"{user_rating}/10" if user_rating not in (None, "") else "нет оценки"
    watched_at = record.get("watched_at") or "не указана"
    if isinstance(watched_at, str) and watched_at:
        from datetime import datetime

        try:
            watched_at = datetime.fromisoformat(watched_at.replace("Z", "+00:00")).strftime("%d.%m.%Y")
        except ValueError:
            pass

    notes = record.get("notes") or "нет отзыва"

    return (
        f"<b>{title}</b> ({year})\n"
        f"Тип: {type_text}\n"
        f"IMDb: {imdb_rating_text}\n"
        f"Жанр: {genre}\n"
        f"Режиссер: {director}\n"
        f"В ролях: {cast}\n"
        f"Описание: {description}\n\n"
        f"Ваша оценка: {user_rating_text}\n"
        f"Дата просмотра: {watched_at}\n"
        f"Отзыв: {notes}\n\n"
        f"Запись {index + 1} из {len(history)}"
    )

def get_watchlist_message(results: List[Dict[str, Any]], page: int) -> str:
    if not results:
        return "Ваш список желаемого пуст."

    safe_page = max(0, min(page, len(results) - 1))
    item = results[safe_page] or {}
    content = item.get("content") or {}

    title = content.get("title") or item.get("content_title") or "Без названия"
    year = content.get("release_year") or "неизвестно"
    imdb_rating = content.get("imdb_rating")
    rating_text = f"{imdb_rating}/10" if imdb_rating not in (None, "") else "нет данных"
    genre = content.get("genre") or "нет данных"
    director = content.get("director") or "нет данных"
    cast = content.get("actors_cast") or content.get("cast") or "нет данных"
    description = content.get("description") or "Описание недоступно"
    content_type = content.get("content_type") or "movie"
    type_text = "фильм" if content_type == "movie" else "сериал"

    if len(description) > 400:
        description = description[:400].rstrip() + "..."

    return (
        f"<b>{title}</b> ({year})\n"
        f"Тип: {type_text}\n"
        f"IMDb: {rating_text}\n"
        f"Жанр: {genre}\n"
        f"Режиссер: {director}\n"
        f"В ролях: {cast}\n"
        f"Описание: {description}\n"
        f"Запись {safe_page + 1} из {len(results)}"
    )

def get_search_results_message(results: List[Dict[str, Any]], page: int) -> str:
    if not results:
        return "По вашему запросу ничего не найдено."

    index = max(0, min(page, len(results) - 1))
    result = results[index]

    title = result.get("title") or "Без названия"
    year = result.get("release_year") or "неизвестно"
    imdb_rating = result.get("imdb_rating")
    rating_text = f"{imdb_rating}/10" if imdb_rating not in (None, "") else "нет данных"
    genre = result.get("genre") or "нет данных"
    director = result.get("director") or "нет данных"
    cast = result.get("cast") or "нет данных"
    description = result.get("description") or "Описание недоступно"

    if len(description) > 600:
        description = description[:600].rstrip() + "..."

    content_type = result.get("content_type") or "movie"
    type_text = "фильм" if content_type == "movie" else "сериал"

    return (
        f"<b>{title}</b> ({year})\n"
        f"Тип: {type_text}\n"
        f"IMDb: {rating_text}\n"
        f"Жанр: {genre}\n"
        f"Режиссер: {director}\n"
        f"В ролях: {cast}\n"
        f"Описание: {description}\n\n"
        f"Результат {index + 1} из {len(results)}"
    )

def get_analytics_message() -> str:
    return (
        "Для подробной статистики перейдите по ссылке http://localhost:8501/"
    )