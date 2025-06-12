# 📦 Standard library
import asyncio
import os

# 🧩 Third-party packages
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.testing.provision import drop_db

# 🏠 Local modules
# from common.bot_cmds_list import private
from database.engine import db
from handlers.admin_private import admin_router
from handlers.user_group import user_group_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession

# 😊 Loading environment variables
load_dotenv(find_dotenv())

# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']


async def on_startup(bot: Bot):
    run_param = False

    # await db.drop_db()

    if run_param:
        await db.drop_db()

    await db.create_db()


async def on_shutdown(bot: Bot):
    try:
        print("Graceful shutdown started...")

        if bot:
            await bot.close()

        if 'db' in globals() and hasattr(db, 'dispose'):
            await db.close()

    except Exception as e:
        print(f"Shutdown error: {e}")
    finally:
        print("Shutdown completed")


async def main():
    bot = Bot(
        token=os.getenv("TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # с версии 3.7.x
    )
    bot.my_admins_list = []
    dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=db.session_maker))

    dp.include_router(user_private_router)
    dp.include_router(user_group_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(private, scope=types.BotCommandScopeAllPrivateChats())
    # allowed updates - используется чтобы Telegram не присылал лишние данные. (message - новые сообщения, edited_message - редактированные сообщения, callback_query - нажатия на кнопки)
    await dp.start_polling(bot, allowed_mentions=dp.resolve_used_update_types())



if __name__ == '__main__':
    asyncio.run(main())
