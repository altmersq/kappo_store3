from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('Каталог').add('Корзина').add('Контакты').add('Информация')

main_adm = ReplyKeyboardMarkup(resize_keyboard=True)
main_adm.add('Каталог').add('Корзина').add('Контакты').add('Информация').add('Управление')
admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Сделать рассылку')

catalog_list = InlineKeyboardMarkup(row_width=3)
catalog_list.add(InlineKeyboardButton(text='Футболки', callback_data='t-shirt'),
                 InlineKeyboardButton(text='Кофты', callback_data='sweatshirts'),
                 InlineKeyboardButton(text='Юбки', callback_data='skirts'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')
