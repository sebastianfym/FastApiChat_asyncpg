from abc import ABC, abstractmethod

import aiohttp
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.config import BASE_URL


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        """Вместо stmt пиши запросики"""
        stmt = insert(self.model).values(**data).returning(self.model.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def edit_one(self, id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def find_all(self):
        stmt = select(self.model)
        results = await self.session.execute(stmt)
        result = [row[0].to_read_model() for row in results.all()]
        return result

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        result = res.scalar_one().to_read_model()
        return result


async def get_user_data(token):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"{BASE_URL}users/users/me/", headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json={}
        ) as resp:
            response = await resp.json()
    return response
