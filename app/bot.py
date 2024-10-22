from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher
from datetime import datetime
from app.handlers import admin_handlers, common_handlers, user_handlers
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database.db import *


async def main():
    load_dotenv()

    # logs for release
    # logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(name)s -
    # %(levelname)s - %(message)s')

    # debug logs
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    db_url = config.db_url

    await init_db()

    engine = create_async_engine(url=db_url, echo=False  )
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    await create_tables(engine)

    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()
    dp["session"] = sessionmaker()
    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    #dp.include_routers(admin_handlers.router, common_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(common_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
