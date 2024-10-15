from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
import app.keyboards.user_keyboards as user_kb
from app.filters.chat_type import ChatTypeFilter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.crud import add_user
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy import text, select, delete


admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]

router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]))


class CatalogStates(StatesGroup):
    choosing_category = State()
    viewing_item = State()
    in_main_menu = State()


class CartStates(StatesGroup):
    viewing_cart = State()
    viewing_item = State()
    checkout = State()


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
    await state.set_state(CatalogStates.choosing_category)


@router.callback_query(CatalogStates.choosing_category, F.data.startswith("category_"))
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

        await send_catalog_item(callback_query.message, item.id, category, session)
        await state.set_state(CatalogStates.viewing_item)
    else:
        await callback_query.message.answer("В этой категории пока нет товаров.")
    await callback_query.answer()


@router.callback_query(CatalogStates.viewing_item, F.data == "next_item")
async def show_next_item(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    current_index = user_data.get("current_index", 0)
    category = user_data.get("category")

    async with session.begin():
        result = await session.execute(
            text("""
                SELECT * FROM catalog 
                WHERE category = :category 
                AND id NOT IN (SELECT product_id FROM cart)
                LIMIT 1 OFFSET :offset
                """),
            {"category": category, "offset": current_index + 1}
        )
        item = result.fetchone()

    if item:
        await state.update_data(current_index=current_index + 1)
        await callback_query.message.delete()
        await send_catalog_item(callback_query.message, item.id, category, session)
    else:
        await callback_query.answer("Это последний товар в этой категории.")


@router.callback_query(CatalogStates.viewing_item, F.data.startswith("add_to_cart_"))
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = callback_query.from_user.id

    async with session.begin():
        result = await session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        )
        user = result.fetchone()

        if not user:
            await callback_query.answer("Пользователь не найден.1")
            return

        user_id = user.id

        item_id = int(callback_query.data.split("_")[3])

        result = await session.execute(
            text("SELECT 1 FROM cart WHERE user_id = :user_id AND product_id = :product_id"),
            {"user_id": user_id, "product_id": item_id}
        )
        item_in_cart = result.scalar()

        if not item_in_cart:
            await session.execute(
                text("INSERT INTO cart (user_id, product_id) VALUES (:user_id, :product_id)"),
                {"user_id": user_id, "product_id": item_id}
            )
            await session.commit()

            await callback_query.answer("Товар добавлен в корзину.")
        else:
            await callback_query.answer("Товар уже в корзине.")

    user_data = await state.get_data()


@router.callback_query(CatalogStates.viewing_item, F.data == "prev_item")
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
            await callback_query.message.delete()
            await send_catalog_item(callback_query.message, item.id, category, session)
        else:
            await callback_query.answer("Это первый товар в этой категории.")
    else:
        await callback_query.answer("Это первый товар в этой категории.")


async def send_catalog_item(message: types.Message, item_id: int, category: str, session: AsyncSession):
    async with session.begin():
        result = await session.execute(
            text("SELECT * FROM catalog WHERE id = :item_id"),
            {"item_id": item_id}
        )
        item = result.fetchone()

        user_id = message.from_user.id
        result = await session.execute(
            text("SELECT 1 FROM cart WHERE user_id = :user_id AND product_id = :product_id"),
            {"user_id": user_id, "product_id": item_id}
        )
        item_in_cart = result.scalar()

    text_msg = f"<b>{item.name}</b>\nЦена: {item.price} руб.\n{item.description}"

    kb = [
        [
            types.InlineKeyboardButton(text="Предыдущий", callback_data="prev_item"),
            types.InlineKeyboardButton(text="Следующий", callback_data="next_item"),
        ],
    ]
    if item_in_cart:
        kb.append([types.InlineKeyboardButton(text="Уже в корзине", callback_data="already_in_cart")])
    else:
        kb.append([types.InlineKeyboardButton(text="В корзину", callback_data=f"add_to_cart_{item.id}")])
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=kb)

    main_menu_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вернуться в главное меню")],
        ],
        resize_keyboard=True
    )

    await message.answer_photo(photo=item.photo, caption=text_msg, reply_markup=inline_kb)
    await message.answer("Вы можете вернуться в главное меню.", reply_markup=main_menu_kb)


@router.message(CatalogStates.viewing_item, F.text == "Вернуться в главное меню")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await message.delete()

    await message.answer("Главное меню", reply_markup=user_kb.main_menu_keyboard())
    await state.set_state(CatalogStates.in_main_menu)


@router.message(F.text.lower() == "корзина")
async def go_to_cart(event, state: FSMContext, session: AsyncSession):
    if isinstance(event, types.Message):
        telegram_id = event.from_user.id
        bot = event.bot
    elif isinstance(event, types.CallbackQuery):
        telegram_id = event.from_user.id
        bot = event.bot
    else:
        return

    async with session.begin():
        result = await session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        )
        user = result.fetchone()

        if not user:
            await bot.send_message(chat_id=telegram_id, text="Пользователь не найден.")
            return

        user_id = user.id

        await state.update_data(user_id=user_id)

        result = await session.execute(
            text("SELECT catalog.id, catalog.name, catalog.price FROM cart "
                 "JOIN catalog ON cart.product_id = catalog.id "
                 "WHERE cart.user_id = :user_id"),
            {"user_id": user_id}
        )
        items = result.fetchall()

    print(items)
    if not items:
        await bot.send_message(chat_id=telegram_id, text="Ваша корзина пуста.")
        return

    total_sum = sum(item.price for item in items)

    items = [dict(item._mapping) for item in items]

    await state.update_data(items=items, current_page=0)
    keyboard = user_kb.cart_keyboard(items=items, page=0)
    await bot.send_message(chat_id=telegram_id, text=f"Ваши товары в корзине (общая сумма: {total_sum} руб.)",
                           reply_markup=keyboard)

    await state.set_state(CartStates.viewing_cart)


@router.callback_query(CartStates.viewing_cart, F.data.in_(["prev_page", "next_page"]))
async def paginate_cart(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = data.get("items")
    current_page = data.get("current_page", 0)

    if callback_query.data == "prev_page":
        current_page -= 1
    elif callback_query.data == "next_page":
        current_page += 1

    await state.update_data(current_page=current_page)
    keyboard = user_kb.cart_keyboard(items, page=current_page)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

    await callback_query.answer()


@router.callback_query(F.data.startswith("view_"))
async def view_cart_item(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    item_id = int(callback_query.data.split("_")[1])

    async with session.begin():
        result = await session.execute(
            text("SELECT * FROM catalog WHERE id = :item_id"), {"item_id": item_id}
        )
        item = result.fetchone()

    if not item:
        await callback_query.message.answer("Товар не найден.")
        return

    text_message = f"<b>{item.name}</b>\nЦена: {item.price} руб.\n{item.description}"

    kb = [
        [types.InlineKeyboardButton(text="Удалить", callback_data=f"remove_from_cart_{item.id}")],
        [types.InlineKeyboardButton(text="Вернуться в корзину", callback_data="back_to_cart")]
    ]
    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=kb)

    if not callback_query.message.photo:
        await callback_query.message.delete()
        await callback_query.message.answer_photo(photo=item.photo, caption=text_message, reply_markup=inline_kb, parse_mode="HTML")
    else:
        await callback_query.message.edit_media(
            types.InputMediaPhoto(media=item.photo, caption=text_message, parse_mode="HTML"),
            reply_markup=inline_kb
        )

    await callback_query.answer()


@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback_query: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if callback_query.from_user:
        item_id = int(callback_query.data.split("_")[3])
        user_data = await state.get_data()
        user_id = user_data.get('user_id')

        if user_id is None:
            await callback_query.answer("Ошибка: Пользователь не найден.")
            return

        async with session.begin():
            await session.execute(
                text("DELETE FROM cart WHERE user_id = :user_id AND product_id = :item_id"),
                {"user_id": user_id, "item_id": item_id}
            )
            await session.commit()

        await callback_query.answer("Товар удален из корзины.")
        await go_to_cart(callback_query, state, session)
    else:
        await callback_query.answer("Произошла ошибка: Неверный запрос.")


@router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await go_to_cart(callback_query, state, session)


@router.callback_query(CartStates.viewing_cart, F.data == "checkout")
async def checkout(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Для оплаты переведите сумму на номер карты: XXXX-XXXX-XXXX-XXXX.\n"
                                           "После оплаты свяжитесь с нами для подтверждения заказа.")
    await state.set_state(CartStates.checkout)


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
