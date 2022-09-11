import os

from unittest.mock import AsyncMock

import pytest
from aiohttp.test_utils import TestClient, loop_context

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


from app.store import Database
from app.store import Store
from app.web.app import setup_app
from app.web.config import Config


@pytest.fixture(scope="session")
def event_loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.store.vk_api = AsyncMock()
    app.store.vk_api.send_message = AsyncMock()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_startup.append(app.store.admins.connect)
    app.on_shutdown.append(app.database.disconnect)

    return app


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture(scope="function", autouse=True)
async def db_session(server):
    real_session = server.database.session
    async with server.database._engine.begin() as conn:
        server.database.session = sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession
        )
        yield server.database.session
        await conn.rollback()
    server.database.session = real_session


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, event_loop, server) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    yield cli
