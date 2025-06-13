from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.formatting import as_marked_section, Bold, as_list
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import get_callback_btns, MenuCallBack
from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def user_private(message: Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, session: AsyncSession, callback_data: MenuCallBack):
    media, reply_markup = await get_menu_content(
        session=session,
        level=callback_data.level,
        menu_name=callback_data.menu_name
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


""" # Все для тестирования, реактивная кнопка
@user_private_router.message(CommandStart())
async def user_private(message: Message):
    await message.answer("Привет, я виртуальный помощник пиццерии! ",
                         reply_markup=get_callback_btns(btns={
                             "Нажми меня": 'some_1',
                         }))


@user_private_router.callback_query(F.data.startswith('some_'))
async def counter(callback: types.CallbackQuery):
    number = int(callback.data.split('_')[-1])

    await callback.message.edit_text(
        text=f"Нажатий - {number}",
        reply_markup=get_callback_btns(btns={
            "Нажми еще раз": f'some_{number + 1}',
        }
    ))
"""

""" Before lesson 8

# 1 method add keyboard
# @user_private_router.message(Command("start"))
# async def start_handler(message: Message):
#     await message.answer("Pizza-bot запущен!", reply_markup=reply.start_kbd)

# 2 method add keyboard
# @user_private_router.message(Command("start"))
# async def start_handler(message: Message):
#     await message.answer("Pizza-bot запущен!",
#                          reply_markup=reply.start_kbd3.as_markup( # can be used start_kbd3
#                              resize_keyboard=True,
#                              input_field_placeholder='Что вас интересует?'
#                          ))
@user_private_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Pizza-bot запущен!",
        reply_markup=get_keyboard(
            "Меню",
            "О пиццерии",
            "Способы доставки",
            "Способы оплаты",
            placeholder="Что вас интересует?",
            sizes=(2, 2),
        ),
    )


@user_private_router.message(Command("help"))
async def start_handler(message: Message):
    await message.answer("Доступные команды:")


@user_private_router.message(F.text.lower() == "меню")
@user_private_router.message(Command("menu"), )
async def start_handler(message: Message, session: AsyncSession):
    # await message.answer("Меню заведения:", reply_markup=reply.remove_kbd)
    for product in await orm_get_products(session):
        caption = (
            f"<strong>{product.name}</strong>\n"
            f"{product.description}\n"
            f"Стоимость: {round(product.price, 2)} $."
        )
        await message.answer_photo(
            product.image,
            caption=caption
        )
    await message.answer("Меню заведения:", reply_markup=types.ReplyKeyboardRemove())


# @user_private_router.message(F.text.lower() == "о нас" or F.text.lower() == "о вас")
@user_private_router.message(F.text.lower().in_(["о нас", "о вас", "о пиццерии"]))
@user_private_router.message(Command("about"))
async def start_handler(message: Message):
    await message.answer("Информация о нас:")


@user_private_router.message((F.text.lower().contains('оплат')) | (F.text.lower() == "способы оплаты"))
@user_private_router.message(Command("pyment"))
async def payment_handler(message: Message):
    text = as_marked_section(
        Bold("Способы оплаты:"),
        "Картой в боте",
        "При получении карта/наличные",
        "В заведении",
        marker='✅ '
    )

    # await message.answer("Способы оплаты:")
    await message.answer(text.as_html())


@user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'способы доставки'))
@user_private_router.message(Command("shipping"))
async def start_handler(message: Message):
    text = as_list(
        as_marked_section(
            Bold("Способы доставки/заказа:"),
            "Курьер",
            "Самовывоз",
            "Покушаю у Вас",
            marker='✅ '
        ),
        as_marked_section(
            Bold("Нельзя"),
            "Почта",
            "Голуби",
            marker='❌ ',
        ),
        sep='\n-----------------------\n'
    )
    await message.answer(text.as_html())

    # await message.answer("<b>Способы доставки:</b>")
    # await message.answer("<b>Способы доставки:</b>", parse_mode=ParseMode.HTML) # перенесли в bot


# @user_private_router.message()
# async def echo_handler(message: Message):
#     await message.answer(f"Echo: {message.text}")


@user_private_router.message(F.contact)
async def get_contact_handler(message: Message):
    await message.answer(f"Номер получены")
    await message.answer(str(message.contact))


@user_private_router.message(F.location)
async def get_location_handler(message: Message):
    await message.answer(f"Локация получена")
    await message.answer(str(message.location))
"""