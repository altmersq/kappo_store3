from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message
from app import keyboards as kb
from app import database as db
from dotenv import load_dotenv
import os

# Инициализация переменных окружения и бота
load_dotenv()
storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(storage=storage)

admin_ids_str = os.getenv('ADMINS')
admin_ids = [int(admin_id) for admin_id in admin_ids_str.split(',')]


async def on_startup(_):
    await db.db_start()
    print('Bot started')


class NewOrder(StatesGroup):
    type = State()
    name = State()
    desc = State()
    price = State()
    photo = State()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    await message.answer(f'Привет, {message.from_user.first_name}, добро пожаловать в kappo store!',
                         reply_markup=kb.main)
    if message.from_user.id in admin_ids:
        await message.answer(f'Вы вошли как администратор', reply_markup=kb.main_adm)


@dp.message(text='Управление')
async def adm(message: types.Message):
    if message.from_user.id in admin_ids:
        await message.answer(f'Привет, {message.from_user.first_name}, ты в панели управления',
                             reply_markup=kb.admin_panel)
    else:
        await message.reply('Я не знаю такой команды')


@dp.message(text='Добавить товар')
async def add_item(message: types.Message):
    if message.from_user.id in admin_ids:
        await NewOrder.type.set()
        await message.answer('Выберите тип товара', reply_markup=kb.catalog_list)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.callback_query(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer('Напишите название товара', reply_markup=kb.cancel)
    await NewOrder.next()


@dp.message(state=NewOrder.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Напишите описание товара')
    await NewOrder.next()


@dp.message(state=NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer('Напишите цену товара')
    await NewOrder.next()


@dp.message(state=NewOrder.price)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await message.answer('Отправьте фотографию товара')
    await NewOrder.next()


@dp.message(lambda message: not message.photo, state=NewOrder.photo)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография')


@dp.message(content_types=['photo'], state=NewOrder.photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await db.add_item(state)
    await message.answer(f'Карточка товара создана!', reply_markup=kb.admin_panel)
    await state.finish()


@dp.message(text='Каталог')
async def catalog(message: types.Message):
    await message.answer(f'Пока здесь ничего нет, но скоро появится!', reply_markup=kb.catalog_list)


@dp.message(text='Информация')
async def catalog(message: types.Message):
    await message.answer(f'Пока здесь ничего нет, но скоро появится!')


@dp.message(text='Корзина')
async def cart(message: types.Message):
    await message.answer(f'Ваша корзина пуста!')


@dp.message(text='Контакты')
async def contacts(message: types.Message):
    await message.answer(f'По всем вопросам обращайтесь к @0')



@dp.message()
async def answer(message: types.Message):
    await message.reply(f'Я не знаю такой команды')


@dp.callback_query()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 't-shirt':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Каталог футболок')
    elif callback_query.data == 'sweatshirts':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Каталог кофт')
    elif callback_query.data == 'skirts':
        await bot.send_message(chat_id=callback_query.from_user.id, text='Каталог юбок')


if __name__ == '__main__':
    dp.start_polling(bot)
