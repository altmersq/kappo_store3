from dotenv import load_dotenv
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("started")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
