from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession):
        self.session = session
