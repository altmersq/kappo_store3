from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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


def category_keyboard():
    kb = [
        [KeyboardButton(text="Футболка")],
        [KeyboardButton(text="Кофта")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите категорию"
    )
    return keyboard