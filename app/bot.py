from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher
from datetime import datetime
from cfg_reader import config
from handlers import admin_handlers, common_handlers, user_handlers


async def main():
    load_dotenv()

    # logs for release
    # logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s -
    # %(levelname)s - %(message)s')
    # debug logs
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    # admin_ids = [int(admin_id) for admin_id in config.admins.split(',')]
    dp.include_routers(admin_handlers.router, common_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
