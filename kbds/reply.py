from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

""" Lesson 5
# method 1
# array in array
start_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Меню"),
            KeyboardButton(text="О пиццерии"),
        ],
        [
            KeyboardButton(text="Способы доставки"),
            KeyboardButton(text="Способы оплаты"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?'
)

remove_kbd = ReplyKeyboardRemove()

# method 2
# для вызова нужно передать дополнительные параметры в handlers
start_kbd2 = ReplyKeyboardBuilder()
start_kbd2.add(
    KeyboardButton(text="Меню"),
    KeyboardButton(text="О пиццерии"),
    KeyboardButton(text="Способы доставки"),
    KeyboardButton(text="Способы оплаты"),
)
start_kbd2.adjust(2, 2)

start_kbd3 = ReplyKeyboardBuilder()
start_kbd3.attach(start_kbd2)
start_kbd3.row(KeyboardButton(text="Оставить отзыв"), )
# start_kbd3.add(
#     KeyboardButton(text="Оставить отзыв"),
# )
# start_kbd3.adjust(2, 2, 1)


test_kbd = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать опрос", request_poll=KeyboardButtonPollType()),
        ],
        [
            KeyboardButton(text="Отправить номер ☎️", request_contact=True),
            KeyboardButton(text="Отправить локацию 📍", request_location=True),
        ]
    ],
    resize_keyboard=True,
)
"""


# Удобство данной функции, не нужно создавать отдельные файлы для handlesr и kbds
def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (1, 1)
):
    """
    Parameters request_contact and request_location must be as indexes of btns args for buttons yout need.
    Example:
    get_keyboard(
        "Меню",
        "О пиццерии",
        "Способы доставки",
        "Способы оплаты",
        placeholder="Что вас интересует?",
        request_contact=4,
        sizes = (2, 2)
    )
    """
    keyboard = ReplyKeyboardBuilder()
    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))

        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )
