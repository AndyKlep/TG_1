import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile
import random
import aiohttp
from weather_api import get_current_weather
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    await dp.start_polling(bot)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Приветики, я бот!")

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help")

@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer('Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ')

@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)

@dp.message(Command('photo'))
async def photo(message: Message):
    list = ['./img/1.jpg','./img/2.jpg','./img/3.jpg',]
    rand_photo = FSInputFile(random.choice(list))
    await message.answer_photo(photo=rand_photo, caption='Это супер крутая картинка')

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

if __name__ == "__main__":
    asyncio.run(main())