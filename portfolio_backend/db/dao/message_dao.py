from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.dao.base_dao import BaseDAO
from portfolio_backend.db.dependencies import get_db_session
from portfolio_backend.db.models.message_model import MessageModel


class MessageDAO(BaseDAO):
    """DAO class for Message."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        super().__init__(session)

    async def get_many_rows(  # type: ignore
        self,
        model_class: type[MessageModel],
        message_by: list[str] | None = None,
        **filters: Any,
    ) -> list[MessageModel | None]:
        """Get multiple rows based on filters and an optional message_by filter."""
        query = select(model_class).filter_by(**filters)

        # Apply the additional filter if message_by is provided
        if message_by:
            query = query.filter(model_class.message_by.in_(message_by))

        query = query.order_by(model_class.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().fetchall())
