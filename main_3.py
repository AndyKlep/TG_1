import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from weather_api import get_current_weather
import aiohttp
import logging
from config import TOKEN
import sqlite3

bot = Bot(token=TOKEN)
dp = Dispatcher()
import keyboard as kb

@dp.message(CommandStart())
async def start(message: Message):
   await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.inline_keyboard_test)

@dp.message(F.text == "Тестовая кнопка 1")
async def test_button(message: Message):
   await message.answer('Обработка нажатия на reply кнопку')

@dp.callback_query(F.data == 'news')
async def news(callback: CallbackQuery):
    await callback.answer("Новости подгружаются", show_alert=True)
    await callback.message.answer('Вот свежие новости!', reply_markup=kb.test_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())