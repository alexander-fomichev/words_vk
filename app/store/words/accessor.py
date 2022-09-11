from typing import Optional

from sqlalchemy import select, delete

from app.base.base_accessor import BaseAccessor
from app.words.models import (
    WordModel,
    SettingModel,
)


class WordsAccessor(BaseAccessor):
    async def create_word(self, title: str, is_correct: bool) -> WordModel:
        new_word = WordModel(title=title, is_correct=is_correct)
        async with self.app.database.session() as session:
            session.add(new_word)
            await session.commit()
        return new_word

    async def delete_word(self, word_id: int) -> int:
        query = delete(WordModel).where(WordModel.id == word_id)
        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
        return word_id

    async def patch_word(
        self, word_id, title: str = None, is_correct: bool = None
    ) -> WordModel:
        query = select(WordModel).where(WordModel.id == word_id)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            word = result.scalar()
            if word:
                if title is not None:
                    word.title = title
                if is_correct is not None:
                    word.is_correct = is_correct
                await session.commit()
        return word

    async def list_words(
        self, is_correct: Optional[bool] = None
    ) -> list[WordModel]:
        query = select(WordModel)
        if is_correct is not None:
            query = query.where(WordModel.is_correct == is_correct)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return list(response.scalars().unique())

    async def get_word_by_title(self, title: str) -> Optional[WordModel]:
        query = select(WordModel).where(WordModel.title == title)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            word = response.scalar()
        if word is None:
            return
        return word

    async def get_word_by_id(self, word_id: int) -> Optional[WordModel]:
        query = select(WordModel).where(WordModel.id == word_id)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            word = response.scalar()
        if word is None:
            return
        return word

    async def create_setting(self, title: str, timeout: int) -> SettingModel:
        new_setting = SettingModel(title=title, timeout=timeout)
        async with self.app.database.session() as session:
            session.add(new_setting)
            await session.commit()
        return new_setting

    async def delete_setting(self, setting_id: int) -> int:
        query = delete(SettingModel).where(SettingModel.id == setting_id)
        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
        return setting_id

    async def patch_setting(
        self, setting_id, title: str = None, timeout: bool = None
    ) -> SettingModel:
        query = select(SettingModel).where(SettingModel.id == setting_id)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            setting = result.scalar()
            if setting:
                if title is not None:
                    setting.title = title
                if timeout is not None:
                    setting.timeout = timeout
                await session.commit()
        return setting

    async def list_settings(self) -> list[SettingModel]:
        query = select(SettingModel)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return list(response.scalars().unique())

    async def get_setting_by_title(self, title: str) -> Optional[SettingModel]:
        query = select(SettingModel).where(SettingModel.title == title)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            setting = response.scalar()
        if setting is None:
            return
        return setting

    async def get_setting_by_id(
        self, setting_id: int
    ) -> Optional[SettingModel]:
        query = select(SettingModel).where(SettingModel.id == setting_id)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            setting = response.scalar()
        if setting is None:
            return
        return setting


