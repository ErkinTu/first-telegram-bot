# 📦 Standard library
import asyncio
import os

# 🧩 Third-party packages
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv, find_dotenv

# 🏠 Local modules
from common.bot_cmds_list import private
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router

# 😊 Loading environment variables
load_dotenv(find_dotenv())


async def main():
    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # с версии 3.7.x
    )
    bot.my_admins_list = []
    dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

    dp.include_router(user_private_router)
    dp.include_router(user_group_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
