import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

async def start_handler(message: Message):
    await message.answer("Бот запущен!")

async def echo_handler(message: Message):
    await message.answer(f"Эхо: {message.text}")

async def main():
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.message.register(echo_handler)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())





