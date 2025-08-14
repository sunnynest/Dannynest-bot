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

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Delete webhook to avoid getUpdates conflict
async def on_startup():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

us
er_states = {}

async def get_chatgpt_response(prompt: str) -> str:
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            n=1,
            temperature=0.7,
        )
        return completion["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "Ошибка обращения к ИИ: {}".format(str(e))

@dp.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer("Бот запущен! Доступные команды:\n"
                         "/order_eggs - заказать яйца\n"
                         "/order_coop - заказать курятник\n"
                         "/remind - установить напоминание\n"
                         "Или просто напишите вопрос, и я отвечу.")

@dp.message(Command("order_eggs"))
async def order_eggs(message: types.Message):
    user_states[message.from_user.id] = {"state": "eggs_pack"}
    await message.answer("Выберите количество коробок яиц:\n"
                         "1 - 12 шт.\n"
                         "2 - 24 шт.\n"
                         "3 - 36 шт.\n"
                         "5 - 60 шт.\n"
                         "6 - 72 шт.\n"
                         "Например, отправьте цифру 2.")

@dp.message(Command("order_coop"))
async def order_coop(message: types.Message):
    user_states[message.from_user.id] = {"state": "coop_details"}
    await message.answer("Опишите параметры курятника (размер, материалы, дополнительные опции).")

@dp.message(Command("remind"))
async def set_reminder(message: types.Message):
    user_states[message.from_user.id] = {"state": "remind_time"}
    await message.answer("Введите напоминание в формате '<минуты> <текст>'.\n"
                         "Например: 10 купить яйца")

@dp.message()
async def handle_message(message: types.Message):
    uid = message.from_user.id
    state_info = user_states.get(uid)
    if state_info:
        state = state_info.get("state")
        if state == "eggs_pack":
            pack = message.text.strip()
            if not pack.isdigit():
                await message.answer("Пожалуйста, укажите число.")
                return
            user_states[uid]["pack"] = pack
            user_states[uid]["state"] = "eggs_color"
            await message.answer("Выберите цвет яиц: белые или жёлтые.")
            return
        elif state == "eggs_color":
            color = message.text.strip().lower()
            pack = user_states[uid].get("pack")
            # Notify admin if configured
            if ADMIN_CHAT_ID:
                await bot.send_message(chat_id=int(ADMIN_CHAT_ID),
                                       text=f"Новый заказ яиц от {message.from_user.full_name}: {pack} коробок, цвет {color}")
            await message.answer(f"Ваш заказ принят: {pack} коробок, цвет {color}.")
            user_states.pop(uid, None)
            return
        elif state == "coop_details":
          
            details = message.text.strip()
            if ADMIN_CHAT_ID:
                await bot.send_message(chat_id=int(ADMIN_CHAT_ID),
                                       text=f"Новый запрос на курятник от {message.from_user.full_name}: {details}")
            await message.answer("Ваш запрос отправлен. Мы свяжемся с вами.")
            user_states.pop(uid, None)
            return
        elif state == "remind_time":
            parts = message.text.strip().split(maxsplit=1)
            if not parts or not parts[0].isdigit() or len(parts) < 2:
                await message.answer("Некорректный формат. Пример: 10 купить яйца")
                user_states.pop(uid, None)
                return
            minutes = int(parts[0])
            reminder_text = parts[1]
            asyncio.create_task(schedule_reminder(minutes, reminder_text, message.chat.id, message.from_user.full_name))
            await message.answer(f"Напоминание установлено через {minutes} мин.")
            user_states.pop(uid, None)
            return
    # Fallback to ChatGPT
    response = await get_chatgpt_response(message.text)
    await message.answer(response)

async def schedule_reminder(minutes: int, text: str, chat_id: int, user_name: str):
    await asyncio.sleep(minutes * 60)
    await bot.send_message(chat_id=chat_id, text=f"Напоминание: {text}")
    if ADMIN_CHAT_ID:
        await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=f"Пользователь {user_name} напоминание: {text}")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
