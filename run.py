import asyncio, os
import uvicorn
from app import app
import bot_multilang_final as bot_module  # если твой файл бота называется иначе — замени здесь

async def start_web():
    port = int(os.getenv("PORT", "8000"))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    await bot_module.main()

async def main():
    await asyncio.gather(start_web(), start_bot())

if __name__ == "__main__":
    asyncio.run(main())
