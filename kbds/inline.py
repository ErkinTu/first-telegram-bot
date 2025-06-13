from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О Нас ℹ️": "about",
        "Оплата 💳": "payment",
        "Доставка 🚚": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()



# def get_url_btns(
#         *,
#         btns: dict[str, str],
#         sizes: tuple[int] = (2,)):
#     keyboard = InlineKeyboardBuilder()
#
#     for text, url in btns.items():
#         keyboard.add(InlineKeyboardButton(text=text, url=url))
#
#     return keyboard.adjust(*sizes).as_markup()
#
#
# # Создать микс из CallBack и URL кнопок
# def get_inlineMix_btns(
#         *,
#         btns: dict[str, str],
#         sizes: tuple[int] = (2,)):
#     keyboard = InlineKeyboardBuilder()
#
#     for text, value in btns.items():
#         if '://' in value:
#             keyboard.add(InlineKeyboardButton(text=text, url=value))
#         else:
#             keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
#
#     return keyboard.adjust(*sizes).as_markup()