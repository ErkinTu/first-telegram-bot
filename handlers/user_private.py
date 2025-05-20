from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

user_private_router = Router()

@user_private_router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Pizza-bot запущен!")

@user_private_router.message()
async def echo_handler(message: Message):
    await message.answer(f"Echo: {message.text}")
