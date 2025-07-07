import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import TOKEN, IMGFLIP_USERNAME, IMGFLIP_PASSWORD

MEME_TEMPLATES = {
    "1": {"id": "61579", "name": "One Does Not Simply"},
    "2": {"id": "112126428", "name": "Distracted Boyfriend"},
    "3": {"id": "87743020", "name": "Two Buttons"}
}

SPACEX_API_URL = "https://api.spacexdata.com/v4"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 *Бот-генератор мемов + SpaceX*\n\n"
        "Доступные команды:\n"
        "/meme - создать мем\n"
        "/launches - последние запуски SpaceX\n"
        "/rockets - список ракет SpaceX",
        parse_mode="Markdown"
    )


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meme_list = "\n".join([f"{key}. {val['name']}" for key, val in MEME_TEMPLATES.items()])
    await update.message.reply_text(f"Выбери номер шаблона мема:\n{meme_list}")
    context.user_data["awaiting_meme_template"] = True


async def handle_meme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    if user_data.get("awaiting_meme_template"):
        chosen_template = update.message.text
        if chosen_template in MEME_TEMPLATES:
            user_data["template_id"] = MEME_TEMPLATES[chosen_template]["id"]
            await update.message.reply_text("🔝 Введи верхнюю строку для мема:")
            user_data["awaiting_top_text"] = True
            user_data["awaiting_meme_template"] = False
        else:
            await update.message.reply_text("❌ Неверный номер. Введи цифру из списка!")

    elif user_data.get("awaiting_top_text"):
        user_data["top_text"] = update.message.text
        await update.message.reply_text("🔽 Теперь введи нижнюю строку:")
        user_data["awaiting_bottom_text"] = True
        user_data["awaiting_top_text"] = False

    elif user_data.get("awaiting_bottom_text"):
        user_data["bottom_text"] = update.message.text

        try:
            response = requests.post(
                "https://api.imgflip.com/caption_image",
                data={
                    "template_id": user_data["template_id"],
                    "username": IMGFLIP_USERNAME,
                    "password": IMGFLIP_PASSWORD,
                    "text0": user_data["top_text"],
                    "text1": user_data["bottom_text"]
                },
                timeout=10
            ).json()

            if response["success"]:
                await update.message.reply_photo(response["data"]["url"])
            else:
                await update.message.reply_text("😢 Ошибка: " + response.get("error_message", "Неизвестная ошибка"))
        except Exception as e:
            await update.message.reply_text("⚠️ Ошибка при создании мема")
            print(f"Meme error: {e}")

        user_data.clear()


async def spacex_launches(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
        # 1. Делаем один четкий запрос
        response = requests.get(
            "https://api.spacexdata.com/v4/launches/latest",
            timeout=10
        )

        # 2. Проверяем ответ
        if response.status_code != 200:
            await update.message.reply_text("🚫 Сервер SpaceX не отвечает")
            return

        launch = response.json()

        # 3. Формируем сообщение
        message = (
            f"🚀 Последний запуск: {launch.get('name', 'Без названия')}\n"
            f"📅 Дата: {launch.get('date_utc', '')[:10]}\n"
            f"🛰️ Ракета: {launch.get('rocket', 'Неизвестна')}\n"
            f"✅ Статус: {'Успех' if launch.get('success') else 'Неудача'}"
        )

        await update.message.reply_text(message)

        # 4. Отправляем ОДНО фото если есть
        if launch.get('links', {}).get('patch', {}).get('large'):
            await update.message.reply_photo(launch['links']['patch']['large'])
        else:
            await update.message.reply_text("📷 Фото не найдено")

    except Exception:
        await update.message.reply_text("⚠️ Ошибка при получении данных")
async def spacex_rockets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список ракет SpaceX"""
    try:
        response = requests.get(f"{SPACEX_API_URL}/rockets")
        rockets = response.json()

        for rocket in rockets:
            name = rocket.get('name', 'Без названия')
            active = "🟢" if rocket.get('active') else "🔴"
            cost = rocket.get('cost_per_launch', 0)

            msg = f"🚀 {name} {active}\n💵 ${cost:,}"
            await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка при получении данных")
        print(f"SpaceX error: {e}")


def main():
    app = Application.builder().token(TOKEN).build()

    # Ваши обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_meme_choice))

    # Новые обработчики SpaceX
    app.add_handler(CommandHandler("launches", spacex_launches))
    app.add_handler(CommandHandler("rockets", spacex_rockets))

    app.run_polling()


if __name__ == "__main__":
    main()