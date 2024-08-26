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

# Хэндлер для обработки выбора категории и отображения первого товара
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

# Хэндлер для обработки нажатия на кнопку "Следующий"
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
            await callback_query.answer("Пользователь не найден.")
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
    #await send_catalog_item(callback_query.message, item_id, user_data['category'], session)


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

# Функция для отправки информации о товаре с кнопками
async def send_catalog_item(message: types.Message, item_id: int, category: str, session: AsyncSession):
    async with session.begin():
        # Получаем информацию о товаре
        result = await session.execute(
            text("SELECT * FROM catalog WHERE id = :item_id"),
            {"item_id": item_id}
        )
        item = result.fetchone()

        # Проверяем, находится ли товар в корзине у текущего пользователя
        user_id = message.from_user.id
        result = await session.execute(
            text("SELECT 1 FROM cart WHERE user_id = :user_id AND product_id = :product_id"),
            {"user_id": user_id, "product_id": item_id}
        )
        item_in_cart = result.scalar()

    # Формируем текст сообщения
    text_msg = f"<b>{item.name}</b>\nЦена: {item.price} руб.\n{item.description}"

    # Инлайн-кнопки для навигации и добавления в корзину
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

    # Обычная клавиатура для возврата в главное меню
    main_menu_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вернуться в главное меню")],
        ],
        resize_keyboard=True
    )

    # Отправляем фото и текст с инлайн-кнопками и обычной клавиатурой
    await message.answer_photo(photo=item.photo, caption=text_msg, reply_markup=inline_kb)
    await message.answer("Вы можете вернуться в главное меню.", reply_markup=main_menu_kb)

# Хэндлер для возврата в главное меню
@router.message(CatalogStates.viewing_item, F.text == "Вернуться в главное меню")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await message.delete()

    await message.answer("Главное меню", reply_markup=user_kb.main_menu_keyboard())
    await state.set_state(CatalogStates.in_main_menu)


@router.message(F.text.lower() == 'корзина')
async def go_to_cart(message: types.Message, session: AsyncSession):
    telegram_id = message.from_user.id

    # Находим id пользователя по telegram_id
    async with session.begin():
        result = await session.execute(
            text("SELECT id FROM users WHERE telegram_id = :telegram_id"),
            {"telegram_id": telegram_id}
        )
        user = result.fetchone()

        if not user:
            await message.answer("Пользователь не найден.")
            return

        user_id = user.id

        # Получаем все товары в корзине пользователя
        result = await session.execute(
            text("""
                SELECT c.id AS cart_id, p.name, p.id AS product_id 
                FROM cart c
                JOIN catalog p ON c.product_id = p.id
                WHERE c.user_id = :user_id
            """),
            {"user_id": user_id}
        )
        items = result.fetchall()

    if not items:
        await message.answer("Ваша корзина пуста.")
        return

        # Формируем сообщение с товарами в корзине и кнопками для их удаления
    message_text = "Ваши товары в корзине:\n\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[])  # Пустой массив передаем для корректного создания объекта

    for item in items:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=f"Убрать {item.name} из корзины", callback_data=f"remove_{item.cart_id}")])

    await message.answer(message_text, reply_markup=kb)


@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback_query: types.CallbackQuery, session: AsyncSession):
    cart_id = int(callback_query.data.split("_")[1])

    async with session.begin():
        # Удаляем товар из корзины
        await session.execute(
            text("DELETE FROM cart WHERE id = :cart_id"),
            {"cart_id": cart_id}
        )
        await session.commit()

    await callback_query.answer("Товар удален из корзины.")

    # Обновляем список товаров в корзине
    await go_to_cart(callback_query.message, session)


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
