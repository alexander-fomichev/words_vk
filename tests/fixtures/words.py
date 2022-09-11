import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.words.models import (

    WordModel, SettingModel)
from tests.utils import clear_table


@pytest.fixture(scope="function")
async def clear_words(db_session: AsyncSession):
    await clear_table(db_session, "WORDS")


@pytest.fixture(scope="function")
async def clear_settings(db_session: AsyncSession):
    await clear_table(db_session, "SETTINGS")


@pytest.fixture
async def word_1(db_session: AsyncSession) -> WordModel:
    title = "олово"
    is_correct = True
    new_word = WordModel(title=title, is_correct=is_correct)
    async with db_session.begin() as session:
        session.add(new_word)

    return WordModel(id=new_word.id, title=title, is_correct=is_correct)


@pytest.fixture
async def word_2(db_session: AsyncSession) -> WordModel:
    title = "олаво"
    is_correct = False
    new_word = WordModel(title=title, is_correct=is_correct)
    async with db_session.begin() as session:
        session.add(new_word)

    return WordModel(id=new_word.id, title=title, is_correct=is_correct)


@pytest.fixture
async def setting_1(db_session: AsyncSession) -> SettingModel:
    title = "настройка 1"
    timeout = 30
    new_setting = SettingModel(title=title, timeout=timeout)
    async with db_session.begin() as session:
        session.add(new_setting)

    return new_setting


@pytest.fixture
async def setting_2(db_session: AsyncSession) -> SettingModel:
    title = "настройка 2"
    timeout = 60
    new_setting = SettingModel(title=title, timeout=timeout)
    async with db_session.begin() as session:
        session.add(new_setting)

    return new_setting
