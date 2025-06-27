import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TOKEN

DB_NAME = "school_data.db"

bot = Bot(token=TOKEN)
dp = Dispatcher()


conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL
)
''')
conn.commit()
conn.close()

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Введите имя:")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите возраст:")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите класс:")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def process_grade(message: Message, state: FSMContext):
    data = await state.get_data()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
        (data['name'], data['age'], message.text)
    )
    conn.commit()
    conn.close()
    await message.answer("Данные сохранены")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

