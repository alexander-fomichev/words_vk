from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database.sqlalchemy_base import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[sessionmaker] = None

    async def connect(self, *_: list, **__: dict) -> None:
        user = self.app.config.database.user
        password = self.app.config.database.password
        host = self.app.config.database.host
        port = self.app.config.database.port
        database = self.app.config.database.database
        DATABASE_URL = (
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        )
        self._db = db
        self._engine = create_async_engine(DATABASE_URL, echo=True, future=True)
        self.session = sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        try:
            await self._engine.dispose()
        except Exception:
            pass


def setup_database(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
