from dotenv import load_dotenv
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject, CommandStart
from datetime import datetime
from cfg_reader import config
import keyboards as kb
from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode


load_dotenv()

# logs for release
#logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# debug logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("started", reply_markup=kb.main_menu_keyboard())
    if message.from_user.id in admin_ids:
        await message.answer("adm mode", reply_markup=kb.main_menu_keyboard_admin())


@dp.message(F.text.lower() == 'каталог')
async def go_to_catalog(message: types.Message):
    await message.answer('В каталоге пока ничего нет')


@dp.message(F.text.lower() == 'корзина')
async def go_to_catalog(message: types.Message):
    await message.answer('В корзине пока ничего нет')


@dp.message(F.text.lower() == 'мой заказ')
async def go_to_catalog(message: types.Message):
    await message.answer('Ваш заказ пуст')


@dp.message(F.text.lower() == 'контакты')
async def go_to_catalog(message: types.Message):
    await message.answer('По всем вопросам обращаться к t.me/0')


@dp.message(F.text.lower() == 'о магазине')
async def go_to_catalog(message: types.Message):
    await message.answer(' ')


@dp.message(F.text.lower() == 'управление')
async def go_to_catalog(message: types.Message):
    if message.from_user.id in admin_ids:
        await message.answer('Панель управления')
    else:
        await message.answer('Я не знаю такой команды', reply_markup=kb.help_inline_keyboard())


@dp.message(Command("adm_info"))
async def adm_info(message: types.Message, started_at: str):
    if message.from_user.id in admin_ids:
        await message.answer(f"Bot started at {started_at}")


@dp.message()
async def unknown_com(message: types.Message):
    await message.answer('Я не знаю такой команды', reply_markup=kb.help_inline_keyboard())



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
