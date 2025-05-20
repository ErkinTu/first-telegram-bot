# 📦 Standard library
import asyncio
import os

# 🧩 Third-party packages
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv

# 🏠 Local modules
from handlers.user_private import user_private_router

# 😊 Loading environment variables
load_dotenv(find_dotenv())


async def main():
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.include_router(user_private_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
