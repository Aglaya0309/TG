import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import aiohttp
from config import TOKEN
from googletrans import Translator

# Настройки
WEATHER_API_KEY = "bff532ac20fe458487263927252506"
CITY = "Krasnodar"
IMG_FOLDER = "img"


# Создаем папку для изображений
os.makedirs(IMG_FOLDER, exist_ok=True)

bot = Bot(token=TOKEN)
dp = Dispatcher()
translator = Translator()


async def get_weather():
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={CITY}&lang=ru"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if "error" in data:
                    return "❌ Ошибка при получении погоды. Попробуйте позже."
                weather = data["current"]["condition"]["text"]
                temp = data["current"]["temp_c"]
                humidity = data["current"]["humidity"]
                wind_speed = data["current"]["wind_kph"]
                return (
                    f"🌦 Погода в Краснодаре:\n"
                    f"🌡 Температура: {temp}°C\n"
                    f"☁ Состояние: {weather}\n"
                    f"💧 Влажность: {humidity}%\n"
                    f"🌬 Ветер: {wind_speed} км/ч"
                )
    except Exception as e:
        return f"⚠ Ошибка подключения к API: {e}"


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я многофункциональный бот.\n"
        "Вот что я умею:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/weather - Погода в Краснодаре\n"
        "/voice - Получить голосовое сообщение\n"
        "Отправьте мне фото - я сохраню его\n"
        "Отправьте текст - я переведу его на английский"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "ℹ Справка по командам:\n"
        "/start - Перезапустить бота\n"
        "/weather - Погода в Краснодаре\n"
        "/voice - Получить голосовое сообщение\n"
        "/help - Эта справка\n\n"
        "Просто отправьте:\n"
        "- Фото - я сохраню его\n"
        "- Текст - я переведу его на английский"
    )


@dp.message(Command("weather"))
async def weather(message: Message):
    weather_info = await get_weather()
    await message.answer(weather_info)


@dp.message(Command('voice'))
async def voice(message: Message):
    voice = FSInputFile("Tenor.ogg")
    await message.answer_voice(voice)


@dp.message(F.photo)
async def save_photo(message: Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path


    file_name = f"{file_id}.jpg"
    save_path = os.path.join(IMG_FOLDER, file_name)
    await bot.download_file(file_path, save_path)

    await message.answer(f"Фото сохранено как {file_name} в папке {IMG_FOLDER}")


@dp.message(F.text)
async def translate_text(message: Message):
    try:
        translation = translator.translate(message.text, dest='en')
        await message.answer(f"Перевод на английский:\n{translation.text}")
    except Exception as e:
        await message.answer(f"Ошибка перевода: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())