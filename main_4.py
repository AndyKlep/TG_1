import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile, CallbackQuery, ReplyKeyboardRemove
from config import TOKEN
from keyboard_for_4 import inline_arkham_keyboard, inline_first_call

bot = Bot(token=TOKEN)
dp = Dispatcher()
import keyboard_for_4 as kb

@dp.message(CommandStart())
async def start(message: Message):
   await message.answer(f'Чего изволите?', reply_markup=kb.start_keys)

@dp.message(F.text == "Привет!")
async def test_button(message: Message):
   await message.answer(f'Привет, {message.from_user.first_name}')

@dp.message(F.text == "Пока!")
async def test_button(message: Message):
   await message.answer(f'Всего доброго, {message.from_user.first_name}', reply_markup=ReplyKeyboardRemove())

@dp.message(Command('links'))
async def links(message: Message):
    await message.answer(f'Основные разделы Arkhamdb', reply_markup=kb.inline_arkham_keyboard)

@dp.message(Command('dynamic'))
async def dynamic(message: Message):
    await message.answer(f'Энтропия!', reply_markup=kb.inline_first_call)

@dp.callback_query(F.data == 'show_more')
async def opt(callback: CallbackQuery):
    await callback.message.answer('Растет!', reply_markup=kb.inline_second_call)
    await callback.answer()

@dp.callback_query(F.data == 'option_1')
async def options_1(callback: CallbackQuery):
    await callback.message.answer('Растет вверх!')

@dp.callback_query(F.data == 'option_2')
async def options_2(callback: CallbackQuery):
    await callback.message.answer('Растет вниз!')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())