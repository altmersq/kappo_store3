from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Основная клавиатура
main_buttons = [
    KeyboardButton('Каталог'),
    KeyboardButton('Корзина'),
    KeyboardButton('Контакты'),
    KeyboardButton('Информация')
]
main = ReplyKeyboardMarkup(keyboard=[main_buttons], resize_keyboard=True)

# Клавиатура для администратора
main_adm_buttons = [
    KeyboardButton('Каталог'),
    KeyboardButton('Корзина'),
    KeyboardButton('Контакты'),
    KeyboardButton('Информация'),
    KeyboardButton('Управление')
]
main_adm = ReplyKeyboardMarkup(keyboard=[main_adm_buttons], resize_keyboard=True)

# Панель администратора
admin_panel_buttons = [
    KeyboardButton('Добавить товар'),
    KeyboardButton('Удалить товар'),
    KeyboardButton('Сделать рассылку')
]
admin_panel = ReplyKeyboardMarkup(keyboard=[admin_panel_buttons], resize_keyboard=True)

t_shirt_button = InlineKeyboardButton(text='Футболки', callback_data='t-shirt')
sweatshirts_button = InlineKeyboardButton(text='Кофты', callback_data='sweatshirts')
skirts_button = InlineKeyboardButton(text='Юбки', callback_data='skirts')

# Создание клавиатуры и добавление кнопок
catalog_list = InlineKeyboardMarkup(row_width=3)
catalog_list.add(t_shirt_button, sweatshirts_button, skirts_button)

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')
