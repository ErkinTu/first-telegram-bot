from aiogram import F
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.orm_query import *
from filters.chat_types import IsAdmin, ChatTypeFilter
from kbds.inline import *
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(IsAdmin(), ChatTypeFilter(["private"]))

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    placeholder="Выбрать действие",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def starring_at_product(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        caption = (
            f"<strong>{product.name}</strong>\n"
            f"{product.description}\n"
            f"Стоимость: {round(product.price, 2)} $."
        )
        await message.answer_photo(
            product.image,
            caption=caption,
            reply_markup=get_callback_btns(btns={
                "Удалить товар": f"delete_{product.id}",
                "Изменить товар": f"update_{product.id}"
            })
        )
    await message.answer("Ок, вот список товаров")


# FSM
class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Введите название товара заново',
        'AddProduct:description': 'Введите описание товара заново',
        'AddProduct:price': 'Введите цену товара заново',
        'AddProduct:image': 'Прикрепите фото товара заново',
    }


@admin_router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer('Введите название товара или напишите "отмена"')
        return

    previous_state = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous_state)
            await message.answer(f"Вы вернулись к прошлому шагу \n {AddProduct.texts[previous_state.state]}")
            return
        previous_state = step


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data({"name": message.text})
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите название товара заново")


@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data({"description": message.text})
    await message.answer("Введите цену товара")
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите описание товара заново")


# Нужна проверка на число
@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data({"price": message.text})
    await message.answer("Прикрепите фото товара")
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите цену товара заново")


@admin_router.message(AddProduct.image, F.photo)
async def add_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()

    try:
        await orm_add_product(session, data)
        await message.answer("Товар успешно добавлен", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении товара: {e}")
        await state.clear()

    # await orm_add_product(session, data)
    # await state.clear()


@admin_router.message(AddProduct.image)
async def add_photo(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, прикрепите фото товара заново")
