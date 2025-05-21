from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Pizza-bot запущен!")


@user_private_router.message(Command("help"))
async def start_handler(message: Message):
    await message.answer("Доступные команды:")


@user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(Command("menu"), )
async def start_handler(message: Message):
    await message.answer("Меню заведения:")


# @user_private_router.message(F.text.lower() == "о нас" or F.text.lower() == "о вас")
@user_private_router.message(F.text.lower().in_(["о нас", "о вас"]))
@user_private_router.message(Command("about"))
async def start_handler(message: Message):
    await message.answer("Информация о нас:")


@user_private_router.message(Command("pyment"))
async def start_handler(message: Message):
    await message.answer("Методы оплаты:")


@user_private_router.message(Command("shipping"))
async def start_handler(message: Message):
    await message.answer("Методы доставки:")


# @user_private_router.message()
# async def echo_handler(message: Message):
#     await message.answer(f"Echo: {message.text}")
