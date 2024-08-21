from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
from app.filters.chat_type import ChatTypeFilter
from app.filters.admin_filters import AdminFilter
from app.models import models
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]
router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]), AdminFilter(admin_ids))
started_at = datetime.now().strftime("%Y-%m-%d %H:%M")


class AddProduct(StatesGroup):
    waiting_for_category = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()


@router.message(F.text.lower() == 'управление')
async def go_to_admin_panel(message: types.Message):
    await message.answer("adm_panel", reply_markup=admin_kb.admin_panel_keyboard())


@router.message(Command("adm_info"))
async def adm_info(message: types.Message, started_at: str):
    await message.answer(f"Bot started at {started_at}")


@router.message(F.text.lower() == 'редактировать каталог')
async def edit_catalog_handler(message: types.Message):
    await message.answer("Выберите действие", reply_markup=admin_kb.edit_catalog_keyboard())


@router.message(F.text.lower() == 'добавить позицию')
async def add_position(message: types.Message, state:FSMContext):
    await message.answer("Выберите категорию товара:", reply_markup=admin_kb.category_keyboard())
    await state.set_state(AddProduct.waiting_for_category)


@router.message(AddProduct.waiting_for_category)
async def category_chosen(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите название товара:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.waiting_for_name)

# Хэндлер для ввода названия
@router.message(AddProduct.waiting_for_name)
async def name_chosen(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара:")
    await state.set_state(AddProduct.waiting_for_description)

# Хэндлер для ввода описания
@router.message(AddProduct.waiting_for_description)
async def description_chosen(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость товара:")
    await state.set_state(AddProduct.waiting_for_price)


@router.message(AddProduct.waiting_for_price)
async def price_chosen(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите цену, используя только цифры.")
        return

    await state.update_data(price=int(message.text))
    await message.answer("Загрузите фото товара:")
    await state.set_state(AddProduct.waiting_for_photo)


@router.message(AddProduct.waiting_for_photo, F.content_type == types.ContentType.PHOTO)
async def photo_chosen(message: types.Message, state: FSMContext, session: AsyncSession):
    print("Photo handler is triggered")
    photo = message.photo[0]
    photo_file_id = photo.file_id

    user_data = await state.get_data()
    category = user_data.get("category")
    name = user_data.get("name")
    description = user_data.get("description")
    price = user_data.get("price")

    async with session.begin():
        new_product = models.Catalog(category=category, name=name, description=description, price=price, photo=photo_file_id)
        session.add(new_product)
        await session.commit()

    await message.answer(f"Товар '{name}' добавлен в каталог.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

