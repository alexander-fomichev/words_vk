from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


def ok_response(data: dict):
    return {
        "status": "ok",
        "data": data,
    }


def error_response(status: str, message: str, data: dict):
    return {
        "status": status,
        "message": message,
        "data": data,
    }


def use_inspector(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


async def check_empty_table_exists(cli, tablename: str):
    engine: AsyncEngine = cli.app.database._engine
    async with engine.begin() as conn:
        tables = await conn.run_sync(use_inspector)

    assert tablename in tables


async def clear_table(db_session: AsyncSession, table: str):
    async with db_session.begin() as session:
        await session.execute(text(f"TRUNCATE {table} CASCADE"))
        await session.execute(
            text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
        )
