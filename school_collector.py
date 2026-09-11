import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from config import TOKEN
import sqlite3

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
	CREATE TABLE IF NOT EXISTS students (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)
	''')
    conn.commit()
    conn.close()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, сейчас я только собираю информацию о студентах!")

@dp.message(Command('add_student'))
async def start(message: Message, state: FSMContext):
    await message.answer("Как зовут студента, которого надо добавить?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    student_name = message.text.strip()

    if not student_name:
        await message.answer("Имя не должно быть пустым. Введите имя ещё раз.")
        return

    conn = sqlite3.connect("school_data.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM students WHERE name = ?",
        (student_name,),
    )

    result = cur.fetchone()
    conn.close()

    if result:
        await message.answer(
            f"Студент с именем {student_name} уже есть."
        )
        await state.clear()
        return

    await state.update_data(name=student_name)
    await message.answer("Сколько ему лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какого он класса?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def city(message: Message, state:FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
       INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
                (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()



init_db()

async def main():
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(main())