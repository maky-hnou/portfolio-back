from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.dao.base_dao import BaseDAO
from portfolio_backend.db.dependencies import get_db_session


class TextDataDAO(BaseDAO):
    """DAO class for TextData."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(session)
