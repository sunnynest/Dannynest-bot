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

# Supported languages dictionary with translations
translations = {
    "ru": {
        "start": "Бот запущен! Доступные команды:\n/order_eggs - заказать яйца\n/order_coop - заказать курятник\n/remind - установить напоминание\n/lang - изменить язык\n\nПиши свой вопрос, и я отвечу.",
        "choose_pack": "Выберите количество коробок с яйцами:\n1 - 12 шт.\n2 - 24 шт.\n3 - 36 шт.\n5 - 60 шт.",
        "invalid_number": "Пожалуйста, укажите число.",
        "choose_color": "Выберите цвет яиц: белые или жёлтые.",
        "confirm_order": "Ваш заказ принят: {pack} коробок, цвет: {color}.",
        "order_sent_admin": "Новый заказ яйца от {user}: {pack} коробок, цвет: {color}.",
        "coop_prompt": "Опишите, какой курятник вам нужен (размер, материалы).",
        "coop_sent_admin": "Новый заказ на курятник от {user}: {details}.",
        "remind_prompt": "Введите количество минут и текст напоминания через пробел (например: 10 купить яйца):",
        "remind_invalid_format": "Неверный формат. Напишите количество минут и текст через пробел.",
        "remind_set": "Напоминание установлено!",
        "reminder_msg": "Напоминание: {text}",
        "error_ai": "Ошибка обращения к ИИ: {error}",
        "language_prompt": "Выберите язык: ru или kk.",
        "language_invalid": "Пожалуйста, укажите 'ru' или 'kk'.",
        "language_set": "Язык установлен: {lang_name}.",
    },
    "kk": {
        "start": "Бот іске қосылды! Қол жетімді командалар:\n/order_eggs - жұмыртқаға тапсырыс беру\n/order_coop - құс қорасына тапсырыс беру\n/remind - еске салғыш орнату\n/lang - тілді өзгерту\n\nСұрағыңыз болса, жазыңыз, мен жауап беремін.",
        "choose_pack": "Жұмыртқа қораптарының санын таңдаңыз:\n1 - 12 дана\n2 - 24 дана\n3 - 36 дана\n5 - 60 дана.",
        "invalid_number": "Өтінемін, сан жазыңыз.",
        "choose_color": "Жұмыртқаның түсін таңдаңыз: ақ немесе сары.",
        "confirm_order": "Сіздің тапсырысыңыз қабылданды: {pack} қорап, түсі {color}.",
        "order_sent_admin": "Жаңа тапсырыс жұмыртқа бойынша {user}: {pack} қорап, түсі {color}.",
        "coop_prompt": "Қандай тауық қорасы сұрауыңыз? (өлшемі, материалдары)",
        "coop_sent_admin": "Жаңа тапсырыс тауық қорасы бойынша {user}: {details}.",
        "remind_prompt": "Минут саны мен еске салу мәтінін бос орын арқылы жазыңыз (мысалы: 10 жұмыртқа алу):",
        "remind_invalid_format": "Формат дұрыс емес. Минут санын және мәтінді бос орын арқылы жазыңыз.",
        "remind_set": "Еске салу орнатылды!",
        "reminder_msg": "Еске салу: {text}",
        "error_ai": "ИИ қызметіне сұрау қатесі: {error}",
        "language_prompt": "Тілді таңдаңыз: ru немесе kk.",
        "language_invalid": "Өтінемін, 'ru' немесе 'kk' көрсетіңіз.",
        "language_set": "Тіл орнатылды: {lang_name}.",
    }
}

# In-memory user state
user_states = {}

def get_user_lang(message: types.Message) -> str:
    uid = message.from_user.id
    state_info = user_states.get(uid)
    if state_info and 'lang' in state_info:
        return state_info['lang']
    code = (message.from_user.language_code or '')[:2].lower()
    return code if code in translations else 'ru'

async def get_chatgpt_response(prompt: str, lang: str) -> str:
    system_prompt = 'Ты полезный ассистент, отвечай на русском языке.' if lang == 'ru' else 'Сен пайдалы көмекшісің, қазақ тілінде жауап бер.'
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt},
    ]
    try:
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return completion['choices'][0]['message']['content'].strip()
    except Exception as e:
        return translations[lang]['error_ai'].format(error=str(e))

@dp.message(CommandStart())
async def on_start(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {'lang': lang}
    await message.answer(translations[lang]['start'])

@dp.message(Command('order_eggs'))
async def order_eggs(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {'lang': lang, 'state': 'eggs_pack'}
    await message.answer(translations[lang]['choose_pack'])

@dp.message(Command('order_coop'))
async def order_coop(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {'lang': lang, 'state': 'coop_details'}
    await message.answer(translations[lang]['coop_prompt'])

@dp.message(Command('remind'))
async def remind(message: types.Message) -> None:
    lang = get_user_lang(message)
    user_states[message.from_user.id] = {'lang': lang, 'state': 'remind_time'}
    await message.answer(translations[lang]['remind_prompt'])

@dp.message(Command('lang'))
async def set_language(message: types.Message) -> None:
    uid = message.from_user.id
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) > 1:
        lang_code = parts[1].lower()
        if lang_code in translations:
            lang_name = 'русский' if lang_code == 'ru' else 'қазақ'
            user_states[uid] = {'lang': lang_code}
            await message.answer(translations[lang_code]['language_set'].format(lang_name=lang_name))
            return
        else:
            current_lang = get_user_lang(message)
            await message.answer(translations[current_lang]['language_invalid'])
            return
    current_lang = get_user_lang(message)
    await message.answer(translations[current_lang]['language_prompt'])

async def schedule_reminder(chat_id: int, delay: float, text: str, lang: str):
    await asyncio.sleep(delay)
    await bot.send_message(chat_id=chat_id, text=translations[lang]['reminder_msg'].format(text=text))
    if ADMIN_CHAT_ID:
        try:
            admin_chat_id = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID.lstrip('-').isdigit() else ADMIN_CHAT_ID
            await bot.send_message(chat_id=admin_chat_id, text=f'\u041d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435 \u0434\u043b\u044f {chat_id}: {text}')
        except Exception:
            pass

@dp.message()
async def handle_message(message: types.Message) -> None:
    uid = message.from_user.id
    state_info = user_states.get(uid, {})
    lang = state_info.get('lang', get_user_lang(message))

    state = state_info.get('state')
    if state == 'eggs_pack':
        pack = message.text.strip()
        if not pack.isdigit():
            await message.answer(translations[lang]['invalid_number'])
            return
        user_states[uid]['pack'] = pack
        user_states[uid]['state'] = 'eggs_color'
        await message.answer(translations[lang]['choose_color'])
        return
    elif state == 'eggs_color':
        color = message.text.strip().lower()
        pack = user_states[uid].get('pack')
        if ADMIN_CHAT_ID:
            try:
                admin_chat_id = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID.lstrip('-').isdigit() else ADMIN_CHAT_ID
                await bot.send_message(chat_id=admin_chat_id, text=translations[lang]['order_sent_admin'].format(user=uid, pack=pack, color=color))
            except Exception:
                pass
        await message.answer(translations[lang]['confirm_order'].format(pack=pack, color=color))
        user_states.pop(uid, None)
        return
    elif state == 'coop_details':
        details = message.text.strip()
        if ADMIN_CHAT_ID:
            try:
                admin_chat_id = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID.lstrip('-').isdigit() else ADMIN_CHAT_ID
                await bot.send_message(chat_id=admin_chat_id, text=translations[lang]['coop_sent_admin'].format(user=uid, details=details))
            except Exception:
                pass
        await message.answer(translations[lang]['remind_set'])
        user_states.pop(uid, None)
        return
    elif state == 'remind_time':
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) != 2 or not parts[0].isdigit():
            await message.answer(translations[lang]['remind_invalid_format'])
            return
        minutes = float(parts[0])
        text = parts[1]
        user_states.pop(uid, None)
        await message.answer(translations[lang]['remind_set'])
        asyncio.create_task(schedule_reminder(message.chat.id, minutes * 60, text, lang))
        return

    response = await get_chatgpt_response(message.text, lang)
    await message.answer(response)

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
