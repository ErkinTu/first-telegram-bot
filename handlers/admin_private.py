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
    "Добавить/изменить баннер",
    placeholder="Выбрать действие",
    sizes=(2, 1),
)


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_update = None

    texts = {
        'AddProduct:name': 'Введите название товара заново',
        'AddProduct:description': 'Введите описание товара заново',
        'AddProduct:category': 'Выберите категория заново',
        'AddProduct:price': 'Введите цену товара заново',
        'AddProduct:image': 'Прикрепите фото товара заново',
    }


@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def admin_features(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f'category_{category.id}' for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('category_')[-1]
    for product in await orm_get_products(session, int(category_id)):
        caption = (
            f"<strong>{product.name}</strong>\n"
            f"{product.description}\n"
            f"Стоимость: {round(product.price, 2)} $."
        )
        await callback.message.answer_photo(
            product.image,
            caption=caption,
            reply_markup=get_callback_btns(btns={
                "Удалить товар": f"delete_{product.id}",
                "Изменить товар": f"update_{product.id}"
            }),
            sizes=(2, 1),
        )
    await callback.message.answer("Ок, вот список товаров")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[-1])
    try:
        await orm_delete_product(session, product_id)
        await callback.answer("Товар успешно удален")
        await callback.message.answer("Товар удален")
    except Exception as e:
        await callback.answer(f"Произошла ошибка при удалении товара: {e}")


# Изменение товара
@admin_router.callback_query(StateFilter(None), F.data.startswith("update_"))
async def update_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = int(callback.data.split("_")[-1])
    product_for_update_ = await orm_get_product(session, product_id)

    AddProduct.product_for_update = product_for_update_
    await callback.answer()
    await callback.message.answer(
        "Введите новое название товара или '.' чтобы оставить как есть\n"
        f"{AddProduct.product_for_update.name}\n"
        f"{AddProduct.product_for_update.description}\n",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# FSM for banners
class AddBanner(StatesGroup):
    image = State()


@admin_router.message(StateFilter(None), F.text == 'Добавить/изменить баннер')
async def add_immage(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Отправьте фото баннера. \nВ описании укажите название для какой страницы: \n{', '.join(pages_names)}\n",
        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_name = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_name:
        await message.answer(f"Введите баннер для одной из страниц: \n{', '.join(pages_name)}\n")
        return
    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Баннер добавлен/изменен", reply_markup=ADMIN_KB)
    await state.clear()


# FSM
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
    if AddProduct.product_for_update:
        AddProduct.product_for_update = None
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


# @admin_router.message(AddProduct.name, F.text)
# async def add_name(message: types.Message, state: FSMContext):
#     await state.update_data({"name": message.text})
#     await message.answer("Введите описание товара")
#     await state.set_state(AddProduct.description)

@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == '.' and AddProduct.product_for_update:
        await state.update_data(name=AddProduct.product_for_update.name)
    else:
        if len(message.text) > 100:
            await message.answer("Название товара слишком длинное, должно быть менее 64 символов\n Введите заново")
            return

        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите название товара заново")


# @admin_router.message(AddProduct.description, F.text)
# async def add_description(message: types.Message, state: FSMContext):
#     await state.update_data({"description": message.text})
#     await message.answer("Введите цену товара")
#     await state.set_state(AddProduct.price)

@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if AddProduct.product_for_update is None:
        description = message.text
        if len(description) > 255:
            await message.answer(
                "Описание товара слишком длинное, должно быть менее 255 символов\nВведите заново"
            )
            return
    else:
        description = (
            AddProduct.product_for_update.description
            if message.text == '.'
            else message.text
        )

        if len(description) > 255:
            await message.answer(
                "Описание товара слишком длинное, должно быть менее 255 символов\nВведите заново"
            )
            return

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.update_data(description=description)
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите описание товара заново")


# Нужна проверка на число
# @admin_router.message(AddProduct.price, F.text)
# async def add_price(message: types.Message, state: FSMContext):
#     await state.update_data({"price": message.text})
#     await message.answer("Прикрепите фото товара")
#     await state.set_state(AddProduct.image)


@admin_router.callback_query(AddProduct.category)
async def add_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Введите цену товара")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите категорию из кнопок')
        await callback.answer()


@admin_router.message(AddProduct.category)
async def add_category(message: types.Message, state: FSMContext):
    await message.answer("Выберите категорию из кнопок")


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == '.' and AddProduct.product_for_update:
        await state.update_data(price=AddProduct.product_for_update.price)
    else:
        try:
            price = float(message.text)
            if price < 0:
                raise ValueError("Цена не может быть отрицательной")
            await state.update_data(price=price)
        except ValueError:
            await message.answer("Цена должна быть числом больше или равным нулю\n Введите заново")
            return

    await message.answer("Прикрепите фото товара")
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите цену товара заново")


# @admin_router.message(AddProduct.image, F.photo)
# async def add_photo(message: types.Message, state: FSMContext, session: AsyncSession):
#     await state.update_data(image=message.photo[-1].file_id)
#     data = await state.get_data()
#
#     try:
#         await orm_add_product(session, data)
#         await message.answer("Товар успешно добавлен", reply_markup=ADMIN_KB)
#         await state.clear()
#
#     except Exception as e:
#         await message.answer(f"Произошла ошибка при добавлении товара: {e}")
#         await state.clear()

# await orm_add_product(session, data)
# await state.clear()

@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    await orm_add_product(session, data)
    await message.answer("Товар успешно добавлен", reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(AddProduct.image)
async def add_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddProduct.product_for_update:
        await state.update_data(image=AddProduct.product_for_update.image)
        data = await state.get_data()
        await orm_update_product(session, AddProduct.product_for_update.id, data)
        await message.answer("Товар успешно изменен", reply_markup=ADMIN_KB)
        AddProduct.product_for_update = None
        await state.clear()
    else:
        await message.answer("Вы ввели не допустимые данные, прикрепите фото товара заново")

# @admin_router.message(AddProduct.image, F.photo)
# async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
#     if message.text == '.':
#         await state.update_data(image=AddProduct.product_for_update.image)
#     else:
#         await state.update_data(image=message.photo[-1].file_id)
#
#     data = await state.get_data()
#
#     try:
#         if AddProduct.product_for_update:
#             await orm_update_product(session, AddProduct.product_for_update.id, data)
#             await message.answer("Товар успешно изменен", reply_markup=ADMIN_KB)
#         else:
#             await orm_add_product(session, data)
#             await message.answer("Товар успешно добавлен", reply_markup=ADMIN_KB)
#         await state.clear()
#     except Exception as e:
#         await message.answer(
#             f"Обратитесь к программисту, он опять хочет денег: \n{e}",
#             reply_markup=ADMIN_KB,
#         )
#         await state.clear()
#
#     AddProduct.product_for_update = None
