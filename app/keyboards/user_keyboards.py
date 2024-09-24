from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

ITEMS_PER_PAGE = 5


def main_menu_keyboard():
    kb = [
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина")],
        [KeyboardButton(text="Мой заказ")],
        [KeyboardButton(text="Контакты")],
        [KeyboardButton(text="О магазине")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   input_field_placeholder="Выберите пункт из меню")
    return keyboard


def help_inline_keyboard():
    kb = [
        [InlineKeyboardButton(text="/help", callback_data="help")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def cart_keyboard(items, page=0):
    """
    Клавиатура для отображения товаров в корзине с кнопками навигации.
    """
    kb = []
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    # Кнопки для товаров
    for item in items[start_index:end_index]:
        kb.append([InlineKeyboardButton(text=f"{item['name']} ({item['price']} руб.)", callback_data=f"view_{item['id']}")])

    # Кнопки навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"))
    if end_index < len(items):
        navigation_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data="next_page"))

    if navigation_buttons:
        kb.append(navigation_buttons)

    # Кнопка оформления
    kb.append([InlineKeyboardButton(text="Перейти к оформлению", callback_data="checkout")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def product_action_keyboard(product_id):
    """
    Клавиатура для отображения действий над товаром (удаление, возврат в корзину).
    """
    kb = [
        [InlineKeyboardButton(text="Удалить", callback_data=f"remove_{product_id}")],
        [InlineKeyboardButton(text="Вернуться в корзину", callback_data="back_to_cart")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)