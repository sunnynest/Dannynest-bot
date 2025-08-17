import asyncio, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from messages import TEXT, LANGS

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def pick_lang(user_code: str) -> str:
    if not user_code:
        return "en"
    code = user_code.split("-")[0].lower()
    if code in LANGS: return code
    # map Telegram codes to supported
    m = {"ru":"ru","uk":"uk","be":"be","es":"es","en":"en"}
    return m.get(code, "en")

def main_menu(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=TEXT["menu"]["eggs"][lang])
    kb.button(text=TEXT["menu"]["coops"][lang])
    kb.button(text=TEXT["menu"]["info"][lang])
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

dp = Dispatcher()

@dp.message(CommandStart())
async def start(m: types.Message):
    lang = pick_lang(m.from_user.language_code)
    await m.answer(TEXT["start"][lang], reply_markup=main_menu(lang))

@dp.message(F.text)
async def router(m: types.Message):
    lang = pick_lang(m.from_user.language_code)
    t = m.text or ""
    if t == TEXT["menu"]["eggs"][lang]:
        await m.answer(TEXT["order_qty"][lang])
        return
    if t.isdigit():
        qty = int(t)
        if qty >= 1:
            await m.answer(TEXT["pickup_or_delivery"][lang])
            return
    if t == TEXT["menu"]["coops"][lang]:
        await m.answer(TEXT["coop_intro"][lang])
        return
    if t == TEXT["menu"]["info"][lang]:
        await m.answer(TEXT["pricing"][lang])
        return
    if "pickup" in t.lower() or "самовывоз" in t.lower() or "самовив" in t.lower():
        await m.answer(TEXT["pickup"][lang])
        return
    if "delivery" in t.lower() or "достав" in t.lower() or "entrega" in t.lower():
        await m.answer(TEXT["delivery"][lang])
        return

async def run():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run())
