import asyncio
import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

if not BOT_TOKEN or " " in BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN отсутствует или указан неверно. Добавьте его в Render > Environment.")

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Supported languages dictionary with translations
translations = {
    "ru": {
        "start": "Бот запущен! Доступные команды:\n/order_eggs - заказать яйца\n/order_coop - заказать курятник\n/remind - установить напоминание\n/lang - сменить язык.",
        "choose_pack": "Выберите количество коробок (1 = 12 шт., 2 = 24 шт., 3 = 36 шт., 5 = 60 шт.).",
        "invalid_number": "Пожалуйста, введите корректное число (1, 2, 3, 5).",
        "choose_color": "Выберите цвет яиц: белый или желтый.",
        "confirm_order": "Ваш заказ: {pack} коробка(и), цвет: {color}.",
        "order_sent_admin": "Ваш заказ отправлен администратору.",
        "coop_prompt": "Опишите желаемый размер и особенности курятника:",
        "coop_sent_admin": "Ваш запрос на курятник отправлен администратору.",
        "remind_prompt": "Введите минуты и текст напоминания через двоеточие, например: '30: проверить яйца'.",
        "remind_invalid_format": "Неверный формат. Используйте 'минуты: текст'.",
        "remind_set": "Напоминание установлено через {minutes} мин.",
        "reminder_msg": "Напоминание: {text}",
        "error_ai": "Ошибка при обращении к ИИ: {error}.",
        "language_prompt": "Выберите язык (en/ru/kk/uk/es):",
        
        "language_invalid": "Недопустимый код языка.",
        "language_set": "Язык установлен на {lang}."
    },
    "kk": {
        "start": "Бот іске косылды! Қол жетімді командалар:\n/order_eggs - жұмыртқа тапсыру\n/order_coop - тауық қорасын тапсыру\n/remind - еске салу орнату\n/lang - тілді өзгерту.",
        "choose_pack": "Қорап санын таңдаңыз (1 = 12 шт., 2 = 24 шт., 3 = 36 шт., 5 = 60 шт.).",
        "invalid_number": "Дұрыс сан енгізіңіз (1, 2, 3, 5).",
        "choose_color": "Жұмыртқаның түсін таңдақыз: ақ немесе сары.",
        "confirm_order": "Сіздің тапсырысыныз: {pack} қорап, түсі: {color}.",
        "order_sent_admin": "Сіздің тапсырысыңыз әкімшіге жіберілді.",
        "coop_prompt": "Қажетті тауық қорасының өлшемін және сипаттамасын жазыңыз:",
        "coop_sent_admin": "Сіздің тауық қорасы бойынша сұранысыңыз әкімшіге жіберілді.",
        "remind_prompt": "Минуттар мен еске салу мәтінін екі нүкте арқылы енгізіңіз, мысалы: '30: жұмыртқаларды тексеру'.",
        "remind_invalid_format": "Формат дұрыс емес. 'минуттар: мәтін' деп жазыңыз.",
        "remind_set": "Еске салу {minutes} минуттан кейін орнатылды.",
        "reminder_msg": "Еске салу: {text}",
        "error_ai": "ЖИ қызметіне сұрау кезінде қате: {error}.",
        "language_prompt": "Тілді таңдаңыз (en/ru/kk/uk/es):",
        "language_invalid": "Тіл коды жарамсыз.",
        "language_set": "Тіл {lang} болып орнатылды."
    },
    "en": {
        "start": "Bot started! Available commands:\n/order_eggs - order eggs\n/order_coop - order a chicken coop\n/remind - set a reminder\n/lang - change language.",
        "choose_pack": "Choose number of boxes (1 = 12 pcs, 2 = 24 pcs, 3 = 36 pcs, 5 = 60 pcs).",
        "invalid_number": "Please enter a valid number (1, 2, 3, 5).",
        "choose_color": "Choose egg color: white or yellow.",
        "confirm_order": "Your order: {pack} box(es), color: {color}.",
        "order_sent_admin": "Your order has been sent to admin.",
        "coop_prompt": "Describe the size and features of the coop you need:",
        "coop_sent_admin": "Your coop request has been sent to admin.",
        "remind_prompt": "Enter minutes and reminder text separated by a colon, e.g. '30: check the chickens'.",
        "remind_invalid_format": "Invalid format. Use 'minutes: text'.",
        "remind_set": "Reminder set in {minutes} minutes.",
        "reminder_msg": "Reminder: {text}",
        "error_ai": "Error contacting AI: {error}.",
        "language_prompt": "Choose language (en/ru/kk/uk/es):",
        "language_invalid": "Invalid language code.",
        "language_set": "Language set to {lang}."
    },
    "uk": {
        "start": "Бот запущено! Доступні команди:\n/order_eggs - замовити яйця\n/order_coop - замовити курник\n/remind - встановити нагадування\n/lang - змінити мову.",
        "choose_pack": "Виберіть кількість коробок (1 = 12 шт., 2 = 24 шт., 3 = 36 шт., 5 = 60 шт.).",
        "invalid_number": "Введіть правильний номер (1, 2, 3, 5).",
        "choose_color": "Оберіть колір яєць: білі або жовті.",
        "confirm_order": "Ваше замовлення: {pack} коробка(и), колір: {color}.",
        "order_sent_admin": "Ваше замовлення надіслано адміністратору.",
        "coop_prompt": "Опишіть розмір та характеристики потрібного курника:",
        "coop_sent_admin": "Ваш запит на курник надіслано адміністратору.",
        "remind_prompt": "Введіть хвилини та текст нагадування через двокрапку, напр. '30: нагодувати курей'.",
        "remind_invalid_format": "Неправильний формат. Введіть 'minutes: text'.",
        "remind_set": "Нагадування встановлено через {minutes} хвилин.",
        "reminder_msg": "Нагадування: {text}",
        "error_ai": "Помилка при з'єднанні з ІІ: {error}.",
        "language_prompt": "Оберіть мову (en/ru/kk/uk/es):",
        "language_invalid": "Неправильний код мови.",
        "language_set": "Мову встановлено на {lang}."
    },
    "es": {
        "start": "¡Bot iniciado! Comandos disponibles:\n/order_eggs - pedir huevos\n/order_coop - pedir gallinero\n/remind - crear recordatorio\n/lang - cambiar idioma.",
        "choose_pack": "Elige cantidad de cajas (1 = 12 uds., 2 = 24 uds., 3 = 36 uds., 5 = 60 uds.).",
        "invalid_number": "Ingrese un número válido (1, 2, 3, 5).",
        "choose_color": "Elige el color de los huevos: blanco o amarillo.",
        "confirm_order": "Tu pedido: {pack} caja(s), color: {color}.",
        "order_sent_admin": "Tu pedido se ha enviado al administrador.",
        "coop_prompt": "Describe el tamaño y características del gallinero que necesitas:",
        "coop_sent_admin": "Tu solicitud de gallinero ha sido enviada al administrador.",
        "remind_prompt": "Ingresa minutos y texto del recordatorio separados por dos puntos, p. ej. '30: alimentar a las gallinas'.",
        "remind_invalid_format": "Formato incorrecto. Usa 'minutos: texto'.",
        "remind_set": "Recordatorio programado en {minutes} minutos.",
        "reminder_msg": "Recordatorio: {text}",
        "error_ai": "Error al contactar la IA: {error}.",
        "language_prompt": "Elige idioma (en/ru/kk/uk/es):",
        "language_invalid": "Código de idioma inválido.",
        "language_set": "El idioma se ha establecido a {lang}."
    }
}

# Dictionary to track user states and selected language
user_states = {}

def get_user_lang(message: types.Message) -> str:
    uid = message.from_user.id
    # Return stored language if set by user
    if uid in user_states and 'lang' in user_states[uid]:
        return user_states[uid]['lang']
    # Use telegram language_code if available else default to 'ru'
    code = message.from_user.language_code or 'ru'
    code = code.split('-')[0]  # use base code, e.g. 'en-US' -> 'en'
    return code if code in translations else 'ru'

async def get_chatgpt_response(prompt: str, lang: str) -> str:
    # Provide system prompt by language to instruct ChatGPT to answer accordingly
    system_prompts = {
        "ru": "Ты помощник сервиса по продаже яиц и курятников. Отвечай всегда на русском языке и помогай по заказу яиц, курятников и рецептам.",
        "kk": "Сен жұмыртқа мен тауық қораларын сату сервисінің көмекшісісің. Әрқашан қазақ тілінде жауап бере және жұмыртқаҚа, тауық қорасына, рецептерге қатысты көмектес.",
        "en": "You are an assistant for an egg and chicken coop sales service. Always respond in English and help with egg orders, coop orders, and recipes.",
        "uk": "Ти помічник сервісу з продажу яєць та курників. Відповідай завжди українською мовою та допомагай замовленням яєць, курників та рецептам.",
        "es": "Eres un asistente de un servicio de venta de huevos y gallineros. Responde siempre en español y ayuda con pedidos de huevos, gallineros y recetas."
    }
    system_prompt = system_prompts.get(lang, system_prompts["ru"])
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

@dp.message(CommandStart())
async def on_start(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang, "state": None}
    await message.answer(translations[lang]["start"])

@dp.message(Command("order_eggs"))
async def order_eggs(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang, "state": "eggs_pack"}
    await message.answer(translations[lang]["choose_pack"])

@dp.message(Command("order_coop"))
async def order_coop(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang, "state": "coop"}
    await message.answer(translations[lang]["coop_prompt"])

@dp.message(Command("remind"))
async def remind(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang, "state": "remind"}
    await message.answer(translations[lang]["remind_prompt"])

@dp.message(Command("lang"))
async def set_language(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang, "state": "set_lang"}
    await message.answer(translations[lang]["language_prompt"])

async def schedule_reminder(chat_id: int, minutes: int, text: str, lang: str):
    await asyncio.sleep(minutes * 60)
    await bot.send_message(chat_id, translations[lang]["reminder_msg"].format(text=text))
    # Notify admin about reminder triggered
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(int(ADMIN_CHAT_ID.lstrip("@")), f"Напоминание для {chat_id}: {text}")
        except Exception:
            pass

@dp.message()
async def handle_message(message: types.Message) -> None:
    uid = message.from_user.id
    lang = get_user_lang(message)
    state = user_states.get(uid, {}).get("state")
    text = message.text.strip()

    if state == "eggs_pack":
        if text not in ["1", "2", "3", "5"]:
            await message.answer(translations[lang]["invalid_number"])
            return
        # Save pack count and ask for color
        user_states[uid]["pack"] = text
        user_states[uid]["state"] = "eggs_color"
        await message.answer(translations[lang]["choose_color"])
        return
    elif state == "eggs_color":
        color = text.lower()
        if color not in ["белый", "желтый", "white", "yellow"]:
            await message.answer(translations[lang]["choose_color"])
            return
        pack = user_states[uid]["pack"]
        # Send order to admin
        if ADMIN_CHAT_ID:
            order_msg = f"Order: {pack} boxes, color: {color}, from user {uid}"
            try:
                await bot.send_message(int(ADMIN_CHAT_ID.lstrip("@")), order_msg)
            except Exception:
                pass
        await message.answer(translations[lang]["confirm_order"].format(pack=pack, color=color))
        await message.answer(translations[lang]["order_sent_admin"])
        user_states[uid]["state"] = None
        return
    elif state == "coop":
        # Forward coop order to admin
        details = text
        if ADMIN_CHAT_ID:
            coop_msg = f"Coop request from {uid}: {details}"
            try:
                await bot.send_message(int(ADMIN_CHAT_ID.lstrip("@")), coop_msg)
            except Exception:
                pass
        await message.answer(translations[lang]["coop_sent_admin"])
        user_states[uid]["state"] = None
        return
    elif state == "remind":
        # Expect 'minutes: text'
        if ":" not in text:
            await message.answer(translations[lang]["remind_invalid_format"])
            return
        parts = text.split(":", 1)
        try:
            minutes = int(parts[0].strip())
            reminder_text = parts[1].strip()
        except ValueError:
            await message.answer(translations[lang]["remind_invalid_format"])
            return
        await message.answer(translations[lang]["remind_set"].format(minutes=minutes))
        asyncio.create_task(schedule_reminder(uid, minutes, reminder_text, lang))
        # Notify admin
        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(int(ADMIN_CHAT_ID.lstrip("@")), f"Reminder set for {uid} in {minutes} minutes: {reminder_text}")
            except Exception:
                pass
        user_states[uid]["state"] = None
        return
    elif state == "set_lang":
        # Set language by user selection
        code = text.lower()
        if code not in translations:
            await message.answer(translations[lang]["language_invalid"])
            return
        user_states[uid]["lang"] = code
        user_states[uid]["state"] = None
        await message.answer(translations[code]["language_set"].format(lang=code))
        return

    # Fallback to ChatGPT
    try:
        response = await get_chatgpt_response(text, lang)
        await message.answer(response)
    except Exception as e:
        await message.answer(translations[lang]["error_ai"].format(error=str(e)))

async def main() -> None:
    # Delete webhook in case it's set
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())import os, sys
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    print("FATAL: BOT_TOKEN is missing or malformed", file=sys.stderr)
    raise SystemExit(1)


