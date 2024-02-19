from dotenv import load_dotenv
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject, CommandStart
from datetime import datetime
from cfg_reader import config
from keyboards import *
from aiogram import F
from aiogram.types import Message
from aiogram.enums import ParseMode


load_dotenv()
#logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("started")
    if message.from_user.id in admin_ids:
        await message.answer("adm mode")


@dp.message(Command("adm_info"))
async def adm_info(message: types.Message, started_at: str):
    if message.from_user.id in admin_ids:
        await message.answer(f"Bot started at {started_at}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
