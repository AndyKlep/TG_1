import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN, THE_CAT_API_KEY
from translator_api import (
    TranslationServiceError,
    translate_ru_to_en,
)


bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

CAT_API_URL = "https://api.thecatapi.com/v1"


def get_cat_breeds() -> list[dict]:
    """
    Получает полный список пород из The Cat API.

    Эта функция синхронная, потому что использует requests.
    Внутри async-обработчика она вызывается через asyncio.to_thread().
    """

    url = f"{CAT_API_URL}/breeds"
    headers = {
        "x-api-key": THE_CAT_API_KEY,
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def get_breed_info(breed_name: str) -> dict | None:
    """
    Ищет породу по точному английскому названию без учёта регистра.

    Например:
    'Maine Coon' -> словарь данных породы.
    """

    breeds = get_cat_breeds()
    normalized_name = breed_name.strip().lower()

    for breed in breeds:
        if breed["name"].lower() == normalized_name:
            return breed

    return None


def get_cat_image_by_breed(breed_id: str) -> str | None:
    """
    Возвращает URL фотографии породы или None,
    если The Cat API не вернул изображений.
    """

    url = f"{CAT_API_URL}/images/search"
    headers = {
        "x-api-key": THE_CAT_API_KEY,
    }
    params = {
        "breed_ids": breed_id,
        "limit": 1,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return data[0].get("url")


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Напиши название породы кошки на русском или английском, "
        "и я пришлю фотографию и описание.\n\n"
        
    )


@dp.message(F.text)
async def send_cat_info(message: Message):
    source_breed_name = message.text.strip()

    if not source_breed_name:
        await message.answer(
            "Введите название породы текстом."
        )
        return

    try:
        translated_breed_name = await asyncio.to_thread(
            translate_ru_to_en,
            source_breed_name,
        )

    except TranslationServiceError as error:
        logging.exception(
            "Ошибка DeepL при переводе названия породы: %s",
            error,
        )

        await message.answer(
            "Не удалось перевести название породы. "
            "Попробуйте написать его на английском, например: "
            "<code>Maine Coon</code>."
        )
        return

    try:
        breed_info = await asyncio.to_thread(
            get_breed_info,
            translated_breed_name,
        )

    except requests.RequestException as error:
        logging.exception(
            "Ошибка запроса к The Cat API: %s",
            error,
        )

        await message.answer(
            "Не удалось подключиться к сервису кошек. "
            "Попробуйте ещё раз позже."
        )
        return

    if breed_info is None:
        await message.answer(
            f"Порода <b>{translated_breed_name}</b> не найдена.\n\n"
            "Попробуйте другое название. Например: "
            "<code>Bengal</code>, <code>Maine Coon</code> "
            "или <code>Sphynx</code>."
        )
        return

    try:
        cat_image_url = await asyncio.to_thread(
            get_cat_image_by_breed,
            breed_info["id"],
        )

    except requests.RequestException as error:
        logging.exception(
            "Ошибка получения изображения из The Cat API: %s",
            error,
        )

        cat_image_url = None

    info = (
        f"🐈 Порода: {breed_info['name']}\n\n"
        f"📖 Описание:\n{breed_info['description']}\n\n"
        f"⏳ Продолжительность жизни: "
        f"{breed_info['life_span']} лет"
    )

    if cat_image_url:
        try:
            await message.answer_photo(
                photo=cat_image_url,
                caption=info,
            )

        except Exception as error:
            logging.exception(
                "Telegram не смог отправить изображение: %s",
                error,
            )

            await message.answer(
                f"{info}\n\n"
                "📷 Данные о породе найдены, но фото "
                "не удалось отправить."
            )

    else:
        await message.answer(
            f"{info}\n\n"
            "📷 К сожалению, The Cat API не вернул "
            "фотографию для этой породы."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())