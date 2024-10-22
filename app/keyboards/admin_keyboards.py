from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

CATEGORIES_PER_PAGE = 7
PRODUCTS_PER_PAGE = 7


def main_menu_keyboard_admin():
    kb = [
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина")],
        [KeyboardButton(text="Мой заказ")],
        [KeyboardButton(text="Контакты")],
        [KeyboardButton(text="О магазине")],
        [KeyboardButton(text="Управление")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   input_field_placeholder="Выберите пункт из меню")
    return keyboard


def admin_panel_keyboard():
    kb = [
        [KeyboardButton(text="Редактировать каталог")],
        [KeyboardButton(text="Создать рассылку")],
        [KeyboardButton(text="Выйти из админ панели")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   input_field_placeholder="Выберите пункт из меню")
    return keyboard


def edit_catalog_keyboard():
    kb = [
        [KeyboardButton(text="Добавить позицию")],
        [KeyboardButton(text="Удалить позицию")],
        # nazad
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
                                   resize_keyboard=True,
                                   input_field_placeholder="Выберите пункт из меню")
    return keyboard


# def category_keyboard():
#     kb = [
#         [KeyboardButton(text="Футболка")],
#         [KeyboardButton(text="Кофта")],
#     ]
#     keyboard = ReplyKeyboardMarkup(
#         keyboard=kb,
#         resize_keyboard=True,
#         input_field_placeholder="Выберите категорию"
#     )
#     return keyboard


def category_keyboard(categories, page=0):
    """
    Клавиатура с категориями и кнопками навигации.
    """
    kb = []
    if not categories:
        kb.append([KeyboardButton(text="Категории отсутствуют. Введите название новой категории.")])
    else:
        start_index = page * CATEGORIES_PER_PAGE
        end_index = start_index + CATEGORIES_PER_PAGE

        for category in categories[start_index:end_index]:
            kb.append([KeyboardButton(text=category)])

        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(KeyboardButton(text="⬅️ Назад"))
        if end_index < len(categories):
            navigation_buttons.append(KeyboardButton(text="➡️ Вперед"))

        if navigation_buttons:
            kb.append(navigation_buttons)

    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите категорию")
    return keyboard


def product_keyboard(products, page=0):
    """
    Клавиатура с товарами и кнопками навигации
    """
    kb = []
    start_index = page * PRODUCTS_PER_PAGE
    end_index = start_index + PRODUCTS_PER_PAGE

    for product in products[start_index:end_index]:
        kb.append([KeyboardButton(text=product)])

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(KeyboardButton(text="⬅️ Назад"))
    if end_index < len(products):
        navigation_buttons.append(KeyboardButton(text="➡️ Вперед"))

    if navigation_buttons:
        kb.append(navigation_buttons)

    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите товар")
    return keyboard
