from typing import Optional, List

from sqlalchemy import select, delete, String
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.words.models import (
    WordModel,
    SettingModel,
    GameModel,
    PlayerModel,
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

    async def patch_word(self, word_id, title: str = None, is_correct: bool = None) -> WordModel:
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

    async def list_words(self, is_correct: Optional[bool] = None) -> list[WordModel]:
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

    async def patch_setting(self, setting_id, title: str = None, timeout: bool = None) -> SettingModel:
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

    async def get_setting_by_id(self, setting_id: int) -> Optional[SettingModel]:
        query = select(SettingModel).where(SettingModel.id == setting_id)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            setting = response.scalar()
        if setting is None:
            return
        return setting

    # async def get_game_by_peer_id(self, peer_id: int) -> Optional[GameModel]:
    #     query = select(GameModel).where(GameModel.peer_id == peer_id)
    #     async with self.app.database.session() as session:
    #         answer = await session.execute(query)
    #         res = answer.scalar()
    #         if res:
    #             return res
    #         return

    async def get_game_by_id(self, id: int) -> Optional[GameModel]:
        query = (
            select(GameModel)
            .where(GameModel.id == id)
            .options(joinedload(GameModel.setting))
            .options(joinedload(GameModel.players))
        )
        async with self.app.database.session() as session:
            answer = await session.execute(query)
            res = answer.scalar()
            if res:
                return res
            return

    async def create_game(self, setting_id: int, peer_id: int) -> GameModel:
        game = GameModel(
            status="init",
            setting_id=setting_id,
            players=[],
            peer_id=peer_id,
            moves_order=None,
            current_move=None,
            event_timestamp=None,
            pause_timestamp=None,
        )
        async with self.app.database.session() as session:
            session.add(game)
            await session.commit()
        return game

    async def list_games(self, peer_id: Optional[int] = None) -> list[GameModel]:
        query = select(GameModel)
        if peer_id is not None:
            query = query.where(GameModel.peer_id == peer_id)
        query = (
            query.options(joinedload(GameModel.players))
            .options(joinedload(GameModel.setting))
            .options(joinedload(GameModel.players))
        )
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return list(response.scalars().unique())

    async def list_active_games(self, peer_id: Optional[int] = None) -> list[GameModel]:
        query = select(GameModel)
        if peer_id is not None:
            query = query.where(
                GameModel.peer_id == peer_id and GameModel.status.astext.cast(String).not_like("finished")
            )
        else:
            query = query.where(GameModel.status.astext.cast(String).not_like("finished"))
        query = (
            query.options(joinedload(GameModel.players))
            .options(joinedload(GameModel.setting))
            .options(joinedload(GameModel.players))
        )
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return list(response.scalars().unique())

    async def clear_game(self, game_id: int) -> int:
        query_delete = delete(PlayerModel).where(PlayerModel.game_id == game_id)
        query = select(GameModel).where(GameModel.id == game_id).options(joinedload(GameModel.setting))
        async with self.app.database.session() as session:
            await session.execute(query_delete)
            result = await session.execute(query)
            game = result.scalar()
            if game:
                game.status = "init"
                game.moves_order = None
                game.event_timestamp = None
                game.current_move = None
                game.pause_timestamp = None
            await session.commit()
        return game

    async def delete_game(self, game_id: int) -> int:
        query = delete(GameModel).where(GameModel.id == game_id)
        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
        return game_id

    async def patch_game(
        self,
        id,
        players: Optional[List[PlayerModel]] = None,
        status: Optional[str] = None,
        moves_order: Optional[str] = None,
        current_move: Optional[int] = None,
        event_timestamp=None,
        pause_timestamp=None,
    ) -> GameModel:
        query = (
            select(GameModel)
            .where(GameModel.id == id)
            .options(joinedload(GameModel.setting))
            .options(joinedload(GameModel.players))
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            game = result.scalar()
            if game:
                if players is not None:
                    game.players = players
                if status is not None:
                    game.status = status
                if moves_order is not None:
                    game.moves_order = moves_order
                if event_timestamp is not None:
                    game.event_timestamp = event_timestamp
                if current_move is not None:
                    game.current_move = current_move
                if pause_timestamp is not None:
                    game.pause_timestamp = pause_timestamp
                await session.commit()
        return game

    async def get_player(self, player_id: int) -> Optional[PlayerModel]:
        query = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            answer = await session.execute(query)
            res = answer.scalar()
            if res:
                return res
            return

    async def create_player(self, game_id: int, user_id: int, name: str) -> PlayerModel:
        player = PlayerModel(
            status="Active",
            online=True,
            name=name,
            game_id=game_id,
            user_id=user_id,
        )
        async with self.app.database.session() as session:
            session.add(player)
            await session.commit()
        return player

    async def list_player(self, game_id) -> list[PlayerModel]:
        query = select(PlayerModel).where(PlayerModel.game_id == game_id)
        async with self.app.database.session() as session:
            response = await session.execute(query)
            return list(response.scalars().unique())

    async def delete_player(self, player_id: int) -> int:
        query = delete(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
        return player_id

    async def patch_player(
        self, player_id: int, online: Optional[bool] = None, status: Optional[str] = None
    ) -> PlayerModel:
        query = select(PlayerModel).where(PlayerModel.id == player_id)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            player = result.scalar()
            if player:
                if online is not None:
                    player.online = online
                if status is not None:
                    player.status = status
                await session.commit()
        return player
