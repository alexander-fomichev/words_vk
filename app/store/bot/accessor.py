import typing
from hashlib import sha256
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameAccessor(BaseAccessor):
    async def get_game_by_peer_id(self, peer_id: str) -> Optional[AdminModel]:
        query = select(GameModel).where(GameModel.peer_id == peer_id)
        async with self.app.database.session() as session:
            answer = await session.execute(query)
            res = answer.scalar()
            if res:
                res
            return

    async def create_game(self, email: str, password: str) -> GameModel:
        admin = AdminModel(
            email=email,
            password=str(sha256(password.encode("utf-8")).hexdigest()),
        )
        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()
        return admin

