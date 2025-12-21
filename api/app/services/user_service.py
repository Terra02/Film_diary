from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging
from app.models.user import User
from app.schemas.user import UserBase

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
   
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"Найден пользователь: id={user.id}, telegram_id={user.telegram_id}")
        else:
            logger.info(f"Пользователь с telegram_id={telegram_id} не найден")
        
        return user


    async def create_user(self, user: UserBase) -> User:
        logger.info(f"Создаём пользователя: {user}")
        telegram_id_str = str(user.telegram_id)

        db_user = User(
            telegram_id=telegram_id_str,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self.db.add(db_user)

        await self.db.commit()
        await self.db.refresh(db_user)
        logger.info(f"Пользовтель создан:id ={db_user.id}")
        return db_user

