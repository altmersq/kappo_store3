from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.cfg_reader import config
from app.models.models import Base


async def create_tables(engine):
    async with engine.begin() as conn:
        # Создаем все таблицы, если они еще не существуют
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы созданы или уже существовали.")


# Функция для создания и возврата асинхронного движка и сессии
def get_engine_and_sessionmaker(db_url):
    engine = create_async_engine(url=db_url, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return engine, sessionmaker


async def init_db():
    db_url = config.db_url
    print(f"Connecting to database: {db_url}")
    engine = create_async_engine(url=db_url, echo=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error occurred during database initialization: {e}")

