from typing import List

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.words.models import WordModel, SettingModel, GameModel, PlayerModel, VoteModel
from tests.utils import clear_table


@pytest.fixture(scope="function")
async def clear_words(db_session: AsyncSession):
    await clear_table(db_session, "WORDS")


@pytest.fixture(scope="function")
async def clear_settings(db_session: AsyncSession):
    await clear_table(db_session, "SETTINGS")


@pytest.fixture(scope="function")
async def clear_games(db_session: AsyncSession):
    await clear_table(db_session, "GAMES")


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


@pytest.fixture
async def game_1(db_session: AsyncSession, setting_1: SettingModel) -> GameModel:
    new_game = GameModel(
        setting_id=setting_1.id,
        peer_id=1,
        status="Init",
        moves_order=None,
        current_move=None,
        event_timestamp=None,
        elapsed_time=0,
        last_word=None,
        vote_word=None
    )
    async with db_session.begin() as session:
        session.add(new_game)
        await session.flush()
        query = select(GameModel).where(GameModel.id == new_game.id).options(joinedload(GameModel.setting)).options(
            joinedload(GameModel.players))
        result = await session.execute(query)
        game = result.scalar()

    return game


@pytest.fixture
async def game_2(db_session: AsyncSession, setting_2: SettingModel) -> GameModel:
    new_game = GameModel(
        setting_id=setting_2.id,
        peer_id=2,
        status="Init",
        moves_order=None,
        current_move=None,
        event_timestamp=None,
        elapsed_time=0,
        last_word=None,
        vote_word=None
    )
    async with db_session.begin() as session:
        session.add(new_game)
        await session.flush()
        query = select(GameModel).where(GameModel.id == new_game.id).options(joinedload(GameModel.setting)).options(
            joinedload(GameModel.players))
        result = await session.execute(query)
        game = result.scalar()

    return game


@pytest.fixture
async def game_3(db_session: AsyncSession, setting_2: SettingModel) -> GameModel:
    new_game = GameModel(
        setting_id=setting_2.id,
        peer_id=3,
        status="Init",
        moves_order=None,
        current_move=None,
        event_timestamp=None,
        elapsed_time=0,
        last_word=None,
        vote_word=None
    )
    async with db_session.begin() as session:
        session.add(new_game)
        await session.flush()
        query = select(GameModel).where(GameModel.id == new_game.id).options(joinedload(GameModel.setting)).options(
            joinedload(GameModel.players))
        result = await session.execute(query)
        game = result.scalar()

    return game


@pytest.fixture
async def player_1(db_session: AsyncSession, game_1: GameModel) -> PlayerModel:
    new_player = PlayerModel(game_id=game_1.id, user_id=1, status="Registered", online=True, name="тест1", score=0)
    async with db_session.begin() as session:
        session.add(new_player)
    return new_player


@pytest.fixture
async def player_2(db_session: AsyncSession, game_2: GameModel) -> PlayerModel:
    new_player = PlayerModel(game_id=game_2.id, user_id=2, status="Registered", online=True, name="тест2", score=0)
    async with db_session.begin() as session:
        session.add(new_player)
    return new_player


@pytest.fixture
async def player_3_4(db_session: AsyncSession, game_3: GameModel) -> List[PlayerModel]:
    players = [
        PlayerModel(game_id=game_3.id, user_id=3, status="Registered", online=True, name="тест3", score=0),
        PlayerModel(game_id=game_3.id, user_id=4, status="Registered", online=True, name="тест4", score=0),
                    ]
    async with db_session.begin() as session:
        session.add_all(players)
    return players


@pytest.fixture
async def vote_1(db_session: AsyncSession, player_1: PlayerModel) -> VoteModel:
    new_vote = VoteModel(game_id=player_1.game_id, player_id=player_1.id, title='зуб', is_correct=True)
    async with db_session.begin() as session:
        session.add(new_vote)
    return new_vote


@pytest.fixture
async def vote_2(db_session: AsyncSession, player_2: PlayerModel) -> VoteModel:
    new_vote = VoteModel(game_id=player_2.game_id, player_id=player_2.id, title='зуб', is_correct=False)
    async with db_session.begin() as session:
        session.add(new_vote)
    return new_vote
