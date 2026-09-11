import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile
import random
import aiohttp
from weather_api import get_current_weather
from config import TOKEN
from translator_api import (
    TranslationServiceError,
    translate_ru_to_en,
)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.full_name}')

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/weather\n/photo")

@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer('Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ')

@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
    await bot.download(message.photo[-1], destination=f'tmp/{message.photo[-1].file_id}.jpg')

@dp.message(Command('photo'))
async def photo(message: Message):
    list = ['./media/1.jpg','./media/2.jpg','./media/3.jpg',]
    rand_photo = FSInputFile(random.choice(list))
    await message.answer_photo(photo=rand_photo, caption='Это супер крутая картинка')

@dp.message(Command('video'))
async def video(message: Message):
    video = FSInputFile('./media/video.mp4')
    await bot.send_chat_action(message.chat.id, 'upload_video')
    await bot.send_video(message.chat.id, video)

@dp.message(Command('audio'))
async def audio(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\\n/start\\n/help\\n/minitraining")

@dp.message(Command("weather"))
async def weather_handler(message: Message, command: CommandObject):
    city = command.args

    if not city:
        await message.answer(
            "Укажите город после команды.\n\n"
            "Пример: <code>/weather Москва</code>"
        )
        return

    try:
        weather = await get_current_weather(city)

    except aiohttp.ClientError:
        await message.answer(
            "Не удалось подключиться к сервису погоды. "
            "Попробуйте ещё раз позже."
        )
        return

    except KeyError:
        await message.answer(
            "Сервис погоды вернул ответ в неожиданном формате. "
            "Попробуйте повторить запрос позже."
        )
        return

    if weather is None:
        await message.answer(
            f"Город <b>{city}</b> не найден. "
            "Попробуйте указать название точнее."
        )
        return

    text = (
        f"📍 {weather['city']}"
        f"{', ' + weather['country'] if weather['country'] else ''}\n\n"
        f"{weather['description']}\n"
        f"🌡 Температура: {weather['temperature']}°C\n"
        f"🤔 Ощущается как: {weather['feels_like']}°C\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"💨 Ветер: {weather['wind_speed']} км/ч"
    )

    await message.answer(text)

@dp.message(Command('voice'))
async def voice(message: Message):
    voice = FSInputFile("./media/sample.ogg")
    await message.answer_voice(voice)

@dp.message(Command("trnsl"))
async def translate_handler(
    message: Message,
    command: CommandObject,
):
    text_to_translate = command.args

    if not text_to_translate:
        await message.answer(
            "Напишите текст после команды.\n\n"
            "Пример:\n"
            "<code>/trnsl Привет! Как дела?</code>"
        )
        return

    try:
        translated_text = await asyncio.to_thread(
            translate_ru_to_en,
            text_to_translate,
        )

    except TranslationServiceError as error:
        print(f"Ошибка перевода: {error}")

        await message.answer(
            "Не удалось перевести текст. "
            "Попробуйте ещё раз позже."
        )
        return

    await message.answer(
        f"🇬🇧Перевод:\n"
        f"{translated_text}"
    )

@dp.message()
async def start(message: Message):
    await message.send_copy(chat_id=message.chat.id)

if __name__ == "__main__":
    asyncio.run(main())