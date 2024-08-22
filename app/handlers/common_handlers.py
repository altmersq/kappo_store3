from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
import app.keyboards.user_keyboards as user_kb
from app.filters.chat_type import ChatTypeFilter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.crud import add_user
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import text


admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]

router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]))


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    await add_user(
        session=session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    await message.answer("started", reply_markup=user_kb.main_menu_keyboard())
    if message.from_user.id in admin_ids:
        await message.answer("adm mode", reply_markup=admin_kb.main_menu_keyboard_admin())


@router.message(F.text.lower() == "каталог")
async def show_catalog(message: types.Message, state: FSMContext, session: AsyncSession):
    async with session.begin():
        result = await session.execute(
            text("SELECT DISTINCT category FROM catalog")
        )
        categories = result.scalars().all()

    kb = [
        [types.InlineKeyboardButton(text=category, callback_data=f"category_{category}")]
        for category in categories
    ]
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer("Выберите категорию:", reply_markup=inline_kb)


@router.callback_query(F.data.startswith("category_"))
async def show_first_item(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    category = callback_query.data.split("_")[1]

    async with session.begin():
        result = await session.execute(
            text("SELECT * FROM catalog WHERE category = :category LIMIT 1"),
            {"category": category}
        )
        item = result.fetchone()

    if item:
        await callback_query.message.delete()
        await state.update_data(current_index=0, category=category)

        await send_catalog_item(callback_query.message, item, session)
    else:
        await callback_query.message.answer("В этой категории пока нет товаров.")
    await callback_query.answer()


@router.callback_query(F.data == "next_item")
async def show_next_item(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    current_index = user_data.get("current_index", 0)
    category = user_data.get("category")

    async with session.begin():
        result = await session.execute(
            text("SELECT * FROM catalog WHERE category = :category LIMIT 1 OFFSET :offset"),
            {"category": category, "offset": current_index + 1}
        )
        item = result.fetchone()

    if item:
        await state.update_data(current_index=current_index + 1)
        await callback_query.message.delete()  # Удаляем предыдущее сообщение
        await send_catalog_item(callback_query.message, item, session)
    else:
        await callback_query.answer("Это последний товар в этой категории.")


@router.callback_query(F.data == "prev_item")
async def show_prev_item(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    current_index = user_data.get("current_index", 0)
    category = user_data.get("category")

    if current_index > 0:
        async with session.begin():
            result = await session.execute(
                text("SELECT * FROM catalog WHERE category = :category LIMIT 1 OFFSET :offset"),
                {"category": category, "offset": current_index - 1}
            )
            item = result.fetchone()

        if item:
            await state.update_data(current_index=current_index - 1)
            await callback_query.message.delete()  # Удаляем предыдущее сообщение
            await send_catalog_item(callback_query.message, item, session)
        else:
            await callback_query.answer("Это первый товар в этой категории.")
    else:
        await callback_query.answer("Это первый товар в этой категории.")


async def send_catalog_item(message: types.Message, item, session: AsyncSession):
    text = f"<b>{item.name}</b>\nЦена: {item.price} руб.\n{item.description}"

    kb = [
        [
            types.InlineKeyboardButton(text="Предыдущий", callback_data="prev_item"),
            types.InlineKeyboardButton(text="Следующий", callback_data="next_item"),
        ],
        [types.InlineKeyboardButton(text="В корзину", callback_data=f"add_to_cart_{item.id}")]
    ]
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=kb)

    main_menu_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вернуться в главное меню")],
        ],
        resize_keyboard=True
    )

    await message.answer_photo(photo=item.photo, caption=text, reply_markup=inline_kb)
    await message.answer("Вы можете вернуться в главное меню.", reply_markup=main_menu_kb)



@router.message(F.text == "Вернуться в главное меню")
async def back_to_main_menu(message: types.Message):
    # Удаляем сообщение с карточкой товара
    await message.delete()

    # Отправляем сообщение с главным меню
    await message.answer("Главное меню", reply_markup=user_kb.main_menu_keyboard())
    if message.from_user.id in admin_ids:
        await message.answer("adm mode", reply_markup=admin_kb.main_menu_keyboard_admin())


@router.message(F.text.lower() == 'корзина')
async def go_to_cart(message: types.Message):
    await message.answer('В корзине пока ничего нет')


@router.message(F.text.lower() == 'мой заказ')
async def go_to_order(message: types.Message):
    await message.answer('Ваш заказ пуст')


@router.message(F.text.lower() == 'контакты')
async def go_to_contacts(message: types.Message):
    await message.answer('По всем вопросам обращаться к t.me/0')


@router.message(F.text.lower() == 'о магазине')
async def go_to_about(message: types.Message):
    await message.answer('about')


# @router.message()
# async def unknown_command(message: types.Message):
#     await message.answer('Я не знаю такой команды', reply_markup=user_kb.help_inline_keyboard())
