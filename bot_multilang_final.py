import os, sys, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# Читаем токен бота из переменных окружения и проверяем корректность
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    print("FATAL: BOT_TOKEN is missing or malformed", file=sys.stderr)
    raise SystemExit(1)

# URL мини‑сайта WebApp (укажите свой домен Render + /app)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://sunnynest-bot.onrender.com/app")

# Список поддерживаемых языков
LANGS = ["en", "ru", "uk", "be", "es"]

# Словарь текстов для разных языков
TEXT = {
    "start": {
        "en": "Welcome to Sunny Nest! Choose an option:",
        "ru": "Добро пожаловать в Sunny Nest! Выберите раздел:",
        "uk": "Ласкаво просимо до Sunny Nest! Оберіть розділ:",
        "be": "Сардэчна запрашаем у Sunny Nest! Абярыце раздзел:",
        "es": "¡Bienvenido a Sunny Nest! Elige una opción:",
    },
    "menu": {
        "eggs": {
            "en": "🥚 Order eggs",
            "ru": "🥚 Заказать яйца",
            "uk": "🥚 Замовити яйця",
            "be": "🥚 Замовіць яйкі",
            "es": "🥚 Pedir huevos",
        },
        "coops": {
            "en": "🏠 Custom coops",
            "ru": "🏠 Курятники на заказ",
            "uk": "🏠 Курники на замовлення",
            "be": "🏠 Курнікі на заказ",
            "es": "🏠 Gallineros a medida",
        },
        "info": {
            "en": "ℹ️ Info & Delivery",
            "ru": "ℹ️ Инфо и доставка",
            "uk": "ℹ️ Інфо та доставка",
            "be": "ℹ️ Інфa і дастаўка",
            "es": "ℹ️ Info y entrega",
        },
        "order_webapp": {
            "en": "🛒 Order (WebApp)",
            "ru": "🛒 Заказ (WebApp)",
            "uk": "🛒 Замовлення (WebApp)",
            "be": "🛒 Замова (WebApp)",
            "es": "🛒 Pedido (WebApp)",
        },
    },
    "pricing": {
        "en": "Price: $5 per 12 eggs. Pickup or delivery (free from 5+ packs). Pay via Cash App: $SirotkinAlexander",
        "ru": "Цена: $5 за 12 яиц. Самовывоз или доставка (бесплатно от 5 упаковок). Оплата: Cash App $SirotkinAlexander",
        "uk": "Ціна: $5 за 12 яєць. Самовивіз або доставка (безкоштовно від 5 упаковок). Оплата: Cash App $SirotkinAlexander",
        "be": "Кошт: $5 за 12 яйкаў. Самавываз або дастаўка (бясплатна ад 5 упак.). Аплата: Cash App $SirotkinAlexander",
        "es": "Precio: $5 por 12 huevos. Retiro o entrega (gratis desde 5 paquetes). Pago: Cash App $SirotkinAlexander",
    },
    "coop_intro": {
        "en": "Describe your coop (size, material, windows, budget). We'll quote and build.",
        "ru": "Опишите желаемый курятник (размер, материал, окна, бюджет). Посчитаем и построим.",
        "uk": "Опишіть бажаний курник (розмір, матеріал, вікна, бюджет). Порахуємо і побудуємо.",
        "be": "Апішыце курнік (памер, матэрыял, вокны, бюджэт). Палічым і пабудуем.",
        "es": "Describe tu gallinero (tamaño, material, ventanas, presupuesto). Cotizamos y construimos.",
    },
}

def pick_lang(code: str | None) -> str:
    """
    Определяем язык пользователя по его языковому коду Telegram.
    Если язык не поддерживается, возвращаем английский.
    """
    if not code:
        return "en"
    parts = code.split("-")
    if parts:
        lang = parts[0].lower()
        if lang in LANGS:
            return lang
    return "en"

def menu(lang: str) -> ReplyKeyboardMarkup:
    """
    Формируем главное меню с кнопками:
      - Заказ через WebApp
      - Заказ яиц (текстовый)
      - Заказ курятников
      - Информация
    """
    kb = [
        [
            KeyboardButton(
                text=TEXT["menu"]["order_webapp"][lang],
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        ],
        [
            KeyboardButton(text=TEXT["menu"]["eggs"][lang]),
            KeyboardButton(text=TEXT["menu"]["coops"][lang]),
        ],
        [KeyboardButton(text=TEXT["menu"]["info"][lang])],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

dp = Dispatcher()

@dp.message(CommandStart())
async def handle_start(m: types.Message):
    """
    /start — приветствуем пользователя и отправляем ему главное меню на его языке.
    """
    lang = pick_lang(m.from_user.language_code)
    await m.answer(TEXT["start"][lang], reply_markup=menu(lang))

@dp.message(F.web_app_data)
async def handle_web_app_data(m: types.Message):
    """
    Принимаем данные из WebApp. Ожидаем JSON с типом заказа "eggs".
    """
    import json
    try:
        data = json.loads(m.web_app_data.data)
        if data.get("type") == "eggs":
            qty = data.get("qty")
            method = data.get("method")
            address = data.get("address") or "-"
            name = data.get("name") or "-"
            phone = data.get("phone") or "-"
            lang = pick_lang(m.from_user.language_code)
            text = (
                f"✅ Заказ принят!\n"
                f"• Дюжин: {qty}\n"
                f"• Способ: {method}\n"
                f"• Адрес: {address}\n"
                f"• Имя/тел: {name} / {phone}\n\n"
                f"{TEXT['pricing'][lang]}"
            )
            await m.answer(text)
        else:
            await m.answer("Received data.")
    except Exception as e:
        await m.answer(f"Bad data: {e}")

@dp.message(F.text)
async def handle_text(m: types.Message):
    """
    Обрабатываем текстовые сообщения: показываем информацию о ценах, курятниках или предлагаем использовать WebApp.
    """
    lang = pick_lang(m.from_user.language_code)
    t = (m.text or "").strip()
    # Обработка раздела "Курятники"
    if t == TEXT["menu"]["coops"][lang]:
        await m.answer(TEXT["coop_intro"][lang])
        return
    # Обработка раздела "Информация"
    if t == TEXT["menu"]["info"][lang]:
        await m.answer(TEXT["pricing"][lang])
        return
    # Обработка заказа яиц: просим использовать WebApp
    if t == TEXT["menu"]["eggs"][lang]:
        await m.answer("Для заказа яиц воспользуйтесь кнопкой «🛒 Order (WebApp)».")
        return

async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise SystemExit("OPENAI_API_KEY environment variable is not set")
openai.api_key = OPENAI_API_KEY



