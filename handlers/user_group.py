from string import punctuation

from aiogram import Router, types, F

from filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))

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
        # Крайняя мера:
        # await message.chat.ban(message.from_user.id)
