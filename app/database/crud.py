from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import models


async def add_user(session: AsyncSession, telegram_id: int, username: str, first_name: str, last_name: str):
    async with session.begin():
        existing_user = await session.execute(select(models.User).where(models.User.telegram_id == telegram_id))
        if existing_user.scalars().first() is None:
            new_user = models.User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(new_user)
            await session.commit()
