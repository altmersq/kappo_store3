from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from app.cfg_reader import config
from app.keyboards import admin_keyboards as admin_kb
import app.keyboards.user_keyboards as user_kb

admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("started", reply_markup=user_kb.main_menu_keyboard())
    if message.from_user.id in admin_ids:
        await message.answer("adm mode", reply_markup=admin_kb.main_menu_keyboard_admin())


@router.message(F.text.lower() == 'каталог')
async def go_to_catalog(message: types.Message):
    await message.answer('В каталоге пока ничего нет')


@router.message(F.text.lower() == 'корзина')
async def go_to_cart(message: types.Message):
    await message.answer('В корзине пока ничего нет')


@router.message(F.text.lower() == 'мой заказ')
async def go_to_order(message: types.Message):
    await message.answer('Ваш заказ пуст')


@router.message(F.text.lower() == 'контакты')
async def go_to_contacts(message: types.Message):
    await message.answer('По всем вопросам обращаться к t.me/0')


@router.message(F.text.lower() == 'о магазине')
async def go_to_about(message: types.Message):
    await message.answer('about')


@router.message()
async def unknown_command(message: types.Message):
    await message.answer('Я не знаю такой команды', reply_markup=user_kb.help_inline_keyboard())
