from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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