import asyncio
import typing
from hashlib import sha256
from typing import Optional

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
        admin = AdminModel(
            email=email,
            password=str(sha256(password.encode("utf-8")).hexdigest()),
        )
        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()
        return admin

    async def connect(self, app: "Application"):
        # while not app.database.session:
        #     await asyncio.sleep(3)
        email = app.config.admin.email
        password = app.config.admin.password
        try:
            user = await self.create_admin(email, password)
            return user
        except IntegrityError as e:
            if e.orig.pgcode == "23505":
                pass
