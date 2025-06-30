import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Привет"), KeyboardButton(text="Пока")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        text="👋 Привет! Я бот с кнопками. Выберите действие:",
        reply_markup=start_keyboard
    )

@dp.message(F.text == "Привет")
async def hello(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")

@dp.message(F.text == "Пока")
async def goodbye(message: Message):
    await message.answer(f"До свидания, {message.from_user.first_name}!")


links_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Новости", url="https://dzen.ru/news?from=rubric&issue_tld=ru")],
        [InlineKeyboardButton(text="Музыка", url="https://music.yandex.ru")],
        [InlineKeyboardButton(text="Видео", url="https://vkvideo.ru/")]
    ]
)

@dp.message(Command("links"))
async def show_links(message: Message):
    await message.answer("Вот полезные ссылки:", reply_markup=links_keyboard)


dynamic_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
    ]
)

expanded_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Опция 1", callback_data="option_1")],
        [InlineKeyboardButton(text="Опция 2", callback_data="option_2")]
    ]
)

@dp.message(Command("dynamic"))
async def show_dynamic(message: Message):
    await message.answer("Динамическая клавиатура:", reply_markup=dynamic_keyboard)

@dp.callback_query(F.data == "show_more")
async def show_more_options(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=expanded_keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("option_"))
async def handle_option(callback: CallbackQuery):
    option = callback.data.split("_")[1]
    await callback.message.answer(f"Вы выбрали: Опция {option}")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())