from string import punctuation

from aiogram import Router, types, F, Bot
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


@user_group_router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == 'creator' or member.status == 'administrator'
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


RESTRICTED_WORDS: set[str] = {
    'тупой', 'тупая', 'тупое', 'тупые', 'тупица'
}


def clean_text(text: str) -> set[str]:
    cleaned = text.translate(str.maketrans('', '', punctuation)).lower()
    return set(cleaned.split())


@user_group_router.message(F.text)
@user_group_router.edited_message(F.text)
async def cleaner_handler(message: types.Message) -> None:
    words_in_message = clean_text(message.text)

    if RESTRICTED_WORDS & words_in_message:
        await message.answer(
            f"{message.from_user.first_name}, соблюдайте порядок в чате!"
        )
        await message.delete()
