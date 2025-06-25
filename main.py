import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import aiohttp
from config import TOKEN

WEATHER_API_KEY = "bff532ac20fe458487263927252506"
CITY = "Krasnodar"

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
        "👋 Привет! Я погодный бот.\n"
            )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "ℹ Справка по командам:\n"
        "/start - Перезапустить бота\n"
        "/weather - Погода в Краснодаре\n"
        "/help - Эта справка"
    )

@dp.message(Command("weather"))
async def weather(message: Message):
    weather_info = await get_weather()
    await message.answer(weather_info)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())