from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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


def help_inline_keyboard():
    kb = [
        [InlineKeyboardButton(text="/help", callback_data="help")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
