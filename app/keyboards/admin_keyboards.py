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
