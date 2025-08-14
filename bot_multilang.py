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
    raise RuntimeError("BOT_TOKEN пустой или указан с пробелами. Задай его в Render > Environment.")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY не установлен. Добавь его в Render > Environment.")

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Supported languages dictionary
translations = {
    "ru": {
        "start": "Бот запущен! Доступные команды:\n/order_eggs - заказать яйца\n/order_coop - заказать курятник\n/remind - установить напоминание\nИли просто напишите вопрос, и я отвечу.",
        "choose_pack": "Выберите количество коробок яиц:\n1 - 12 шт.\n2 - 24 шт.\n3 - 36 шт.\n5 - 60 шт.",
        "invalid_number": "Пожалуйста, укажите число.",
        "choose_color": "Выберите цвет яиц: белые или жёлтые.",
        "confirm_order": "Ваш заказ принят: {pack} коробок, цвет {color}.",
        "order_sent_admin": "Новый заказ яиц от {user}: {pack} коробок, цвет {color}",
        "coop_prompt": "Опишите, какой курятник вам нужен (размер, материалы):",
        "coop_sent_admin": "Новый запрос на курятник от {user}: {details}",
        "remind_prompt": "Введите количество минут и текст напоминания через пробел (\u043dапример: 10 купить яйца):",   
        "remind_invalid_format": "Неверный формат. Напишите количество минут и текст через пробел.",
        "remind_set": "Напоминание установлено!", 
        "reminder_msg": "Напоминание: {text}",
        "error_ai": "Ошибка обращения к ИИ: {error}",
    },
    "kk": {
        "start": "Бот іске қосылды! Қол жетімді командалар:\n/order_eggs - жұмыртқаға тапсырыс беру\n/order_coop - тауық қорасына тапсырыс беру\n/remind - еске салуды орнату\nНемесе сұрақ жазсаңыз, мен жауап беремін.",
        "choose_pack": "Жұмыртқа қораптарының санын таңдаңыз:\n1 - 12 дана\n2 - 24 дана\n3 - 36 дана\n5 - 60 дана",
        "invalid_number": "Өтінемін, сан жазыңыз.",
        "choose_color": "Жұмыртқаның түсін таңдаңыз: ақ немесе сары.",
        "confirm_order": "Сіздің тапсырысыңыз қабылданды: {pack} қорап, түсі {color}.",
        "order_sent_admin": "Жаңа жұмыртқа тапсырысы {user}: {pack} қорап, түсі {color}",
        "coop_prompt": "Қандай тауық қорасы керек енін сипаттаңыз (өлшемі, материалы):",
        "coop_sent_admin": "Жаңа тауық қорасы сұрауы {user}: {details}",
        "remind_prompt": "Минут саны мен еске салу мәтінін бос орын арқылы жазыңыз (\u043cысалы: 10 жұмыртқа алу):",
        "remind_invalid_format": "Формат дұрыс емес. Минут саны мен мәтінді бос орын арқылы жазыңыз.",
        "remind_set": "Еске салу орнатылды!",
        "reminder_msg": "Еске салу: {text}",
        "error_ai": "ИИ қызметіне сұраныс қатесі: {error}",
    }
}

user_states = {}

def get_user_lang(message: types.Message) -> str:
    code = (message.from_user.language_code or "").split("-")[0].lower()
    return code if code in translations else "ru"

async def get_chatgpt_response(prompt: str, lang: str) -> str:
    system_prompt = "Ты полезный ассистент, отвечай на русском языке." if lang == "ru" else "Сен пайдалы көмекшісің, жауаптарыңды қазақ тілінде бер."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return translations[lang]["error_ai"].format(error=str(e))

@dp.message(CommandStart())
async def on_start(message: types.Message):
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"lang": lang}
    await message.answer(translations[lang]["start"])

@dp.message(Command("order_eggs"))
async def order_eggs(message: types.Message):
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"state": "eggs_pack", "lang": lang}
    await message.answer(translations[lang]["choose_pack"])

@dp.message(Command("order_coop"))
async def order_coop(message: types.Message):
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"state": "coop_details", "lang": lang}
    await message.answer(translations[lang]["coop_prompt"])

@dp.message(Command("remind"))
async def remind(message: types.Message):
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {"state": "remind_time", "lang": lang}
    await message.answer(translations[lang]["remind_prompt"])

async def schedule_reminder(chat_id, delay, text, lang):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=chat_id, text=translations[lang]["reminder_msg"].format(text=text))
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c {chat_id} \u043f\u043e\u043b\u0443\u0447\u0438\u043b \u043d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435: {text}")

@dp.message()
async def handle_message(message: types.Message):
    uid = message.from_user.id
    state_info = user_states.get(uid)
    lang = state_info.get("lang") if state_info else get_user_lang(message)
    if state_info:
        state = state_info.get("state")
        if state == "eggs_pack":
            pack = message.text.strip()
            if not pack.isdigit():
                await message.answer(translations[lang]["invalid_number"])
                return
            user_states[uid]["pack"] = pack
            user_states[uid]["state"] = "eggs_color"
            await message.answer(translations[lang]["choose_color"])
            return
        elif state == "eggs_color":
            color = message.text.strip().lower()
            pack = user_states[uid].get("pack")
            if ADMIN_CHAT_ID:
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=translations[lang]["order_sent_admin"].format(user=message.from_user.full_name, pack=pack, color=color))
            await message.answer(translations[lang]["confirm_order"].format(pack=pack, color=color))
            user_states.pop(uid, None)
            return
        elif state == "coop_details":
            details = message.text.strip()
            if ADMIN_CHAT_ID:
                await bot.send_message(chat_id=ADMIN_CHA_ID, text=translations[lang]["coop_sent_admin"].format(user=message.from_user.full_name, details=details))
            # Send a thank-you message
            thank_you = "\u0421\u043f\u0430\u0441\u0438\u0431\u043e \u0437\u0430 \u0437\u0430\u043f\u0440\u043e\u0441! \u041c\u044b \u0441 \u0432\u0430\u043c\u0438 \u0441\u0432\u044f\u0436\u0435\u043c\u0441\u044f \u0432 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0432\u0440\u0435\u043c\u044f." if lang == "ru" else "\u0421\u04b1\u0440\u0430\u0443\u044b\u04a3\u044b\u04a3\u044b\u0437 \u04af\u0448\u0456\u043d \u0440\u0430\u049b\u043c\u0435\u0442! \u0411\u0456\u0437 \u0441\u0456\u0437\u0431\u0435\u043d \u0436\u0430\u049b\u044b\u043d \u0430\u0440\u0430\u0434\u0430 \u0445\u0430\u0431\u0430\u0440\u043b\u0430\u0441\u0430\u043c\u044b\u0437."
            await message.answer(thank_you)
            user_states.pop(uid, None)
            return
        elif state == "remind_time":
            parts = message.text.strip().split(maxsplit=1)
            if len(parts) < 2 or not parts[0].isdigit():
                await message.answer(translations[lang]["remind_invalid_format"])
                return
            minutes = int(parts[0])
            text = parts[1]
            await message.answer(translations[lang]["remind_set"])
            asyncio.create_task(schedule_reminder(message.chat.id, minutes*60, text, lang))
            user_states.pop(uid, None)
            return
    # fallback to AI chat
    response = await get_chatgpt_response(message.text, lang)
    await message.answer(response)

async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
