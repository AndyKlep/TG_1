import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from config import TOKEN
from kitsu_api import (
    KitsuAPIError,
    get_random_anime,
    get_top_anime,
    get_top_anime_by_year,
)


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


def shorten_text(
    text: str,
    max_length: int = 900,
) -> str:
    """
    Обрезает длинное описание, чтобы caption фотографии
    не стал слишком длинным для Telegram.
    """

    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(" ", 1)[0] + "…"


def format_anime(anime: dict) -> str:
    """
    Формирует подпись/текст для сообщения Telegram.
    """

    rank = anime["popularity_rank"]

    rank_text = (
        f"#{rank}"
        if rank is not None
        else "Не указано"
    )

    description = shorten_text(
        anime["description"]
    )

    return (
        f"🎬 <b>{anime['title']}</b>\n\n"
        f"📅 <b>Год выхода:</b> {anime['year']}\n"
        f"🔥 <b>Место в популярности:</b> {rank_text}\n\n"
        f"📖 <b>Описание:</b>\n"
        f"{description}"
    )


async def send_anime(
    message: Message,
    anime: dict,
):
    """
    Отправляет фотографию постера с подписью.
    Если изображения нет или Telegram не может его скачать,
    отправляет только текст.
    """

    text = format_anime(anime)
    image_url = anime["image_url"]

    if image_url:
        try:
            await message.answer_photo(
                photo=image_url,
                caption=text,
            )
            return

        except Exception:
            logging.exception(
                "Не удалось отправить постер аниме: %s",
                image_url,
            )

    await message.answer(text)


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Я бот для поиска информации об аниме через Kitsu API.\n\n"
        "Доступные команды:\n"
        "🎲 <code>/random</code> — случайное аниме\n"
        "🏆 <code>/top 1</code> — аниме на указанном месте "
        "в общем рейтинге популярности\n"
        "📅 <code>/top_year 1 2024</code> — аниме на указанном "
        "месте среди вышедших в указанном году\n\n"
        "Примеры:\n"
        "<code>/top 10</code>\n"
        "<code>/top_year 5 2020</code>"
    )


@dp.message(Command("random"))
async def random_command(message: Message):
    await message.answer("🎲 Подбираю случайное аниме...")

    try:
        anime = await get_random_anime()

    except KitsuAPIError as error:
        logging.exception("Ошибка Kitsu API: %s", error)

        await message.answer(
            "Не удалось получить данные от Kitsu API. "
            "Попробуйте ещё раз позже."
        )
        return

    if anime is None:
        await message.answer(
            "Не удалось найти случайное аниме. "
            "Попробуйте выполнить команду ещё раз."
        )
        return

    await send_anime(message, anime)


@dp.message(Command("top"))
async def top_command(
    message: Message,
    command: CommandObject,
):
    if not command.args:
        await message.answer(
            "Укажите позицию в рейтинге.\n\n"
            "Пример: <code>/top 1</code>"
        )
        return

    try:
        position = int(command.args.strip())

    except ValueError:
        await message.answer(
            "Позиция должна быть целым числом.\n\n"
            "Пример: <code>/top 10</code>"
        )
        return

    if position < 1:
        await message.answer(
            "Позиция должна быть больше или равна 1."
        )
        return

    await message.answer(
        f"🏆 Ищу аниме на позиции {position}..."
    )

    try:
        anime = await get_top_anime(position)

    except KitsuAPIError as error:
        logging.exception("Ошибка Kitsu API: %s", error)

        await message.answer(
            "Не удалось получить данные от Kitsu API. "
            "Попробуйте ещё раз позже."
        )
        return

    if anime is None:
        await message.answer(
            f"Аниме на позиции {position} не найдено."
        )
        return

    await send_anime(message, anime)


@dp.message(Command("top_year"))
async def top_year_command(
    message: Message,
    command: CommandObject,
):
    if not command.args:
        await message.answer(
            "Используйте команду в формате:\n"
            "<code>/top_year НОМЕР ГОД</code>\n\n"
            "Пример: <code>/top_year 1 2024</code>"
        )
        return

    arguments = command.args.split()

    if len(arguments) != 2:
        await message.answer(
            "Нужно указать ровно два числа: место и год.\n\n"
            "Пример: <code>/top_year 5 2020</code>"
        )
        return

    try:
        position = int(arguments[0])
        year = int(arguments[1])

    except ValueError:
        await message.answer(
            "Место и год должны быть целыми числами.\n\n"
            "Пример: <code>/top_year 5 2020</code>"
        )
        return

    if position < 1:
        await message.answer(
            "Позиция должна быть больше или равна 1."
        )
        return

    if not 1900 <= year <= 2100:
        await message.answer(
            "Укажите корректный год, например: <code>2024</code>."
        )
        return

    await message.answer(
        f"📅 Ищу аниме №{position} по популярности "
        f"среди релизов {year} года..."
    )

    try:
        anime = await get_top_anime_by_year(
            position=position,
            year=year,
        )

    except KitsuAPIError as error:
        logging.exception("Ошибка Kitsu API: %s", error)

        await message.answer(
            "Не удалось получить данные от Kitsu API. "
            "Попробуйте ещё раз позже."
        )
        return

    if anime is None:
        await message.answer(
            f"Для {year} года не найдено аниме "
            f"на позиции {position}."
        )
        return

    await send_anime(message, anime)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())