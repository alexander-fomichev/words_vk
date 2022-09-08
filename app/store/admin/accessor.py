import asyncio
import typing
from hashlib import sha256
from typing import Optional

from asyncpg import UniqueViolationError
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> Optional[AdminModel]:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            answer = await session.execute(query)
            res = answer.first()
            if res:
                return res[0]
            return

    async def create_admin(self, email: str, password: str) -> AdminModel:
        # pass
        query = insert(AdminModel).values(
            email=email, password=str(sha256(password.encode("utf-8")).hexdigest())
        )
        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def connect(self, app: "Application"):
        while not app.database.session:
            await asyncio.sleep(3)
        email = app.config.admin.email
        password = app.config.admin.password
        try:
            await self.create_admin(email, password)
        except IntegrityError:
            pass
