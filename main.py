import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def start(message: Message):
    await message.answer("Привет! Это Sunny Nest бот 🐣")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
