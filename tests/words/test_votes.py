from dataclasses import asdict

from sqlalchemy import delete
from sqlalchemy.future import select

from app.words.models import VoteModel, GameModel, PlayerModel
from app.store import Store
from tests.utils import check_empty_table_exists
from tests.utils import ok_response


class TestVoteStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "votes")

    async def test_create_vote(self, cli, store: Store, clear_games, clear_settings, player_1: PlayerModel):
        vote = await store.words.create_vote(
            player_id=player_1.id,
            game_id=player_1.game_id,
            title='сом',
            is_correct=True
        )
        assert type(vote) is VoteModel

        async with cli.app.database.session() as session:
            res = await session.execute(select(VoteModel))
            votes = res.scalars().all()

        assert len(votes) == 1
        async with cli.app.database.session() as session:
            res = await session.execute(
                select(VoteModel).where(VoteModel.title == 'сом')
            )
            new_vote = res.scalar()
        assert new_vote.player_id == player_1.id
        assert new_vote.game_id == player_1.game_id
        assert new_vote.is_correct == True

    # async def test_get_game_by_id(
    #         self, store: Store, game_1: GameModel
    # ):
    #     game = await store.words.get_game_by_id(game_1.id)
    #     assert game == game_1

    async def test_list_votes(
            self,
            cli,
            store: Store,
            clear_settings,
            clear_games,
            vote_1: VoteModel,
            vote_2: VoteModel,
    ):
        votes = await store.words.list_votes(vote_1.game_id, vote_1.title)
        assert len(votes) == 1
        assert vote_1 in votes


    async def test_delete_vote(
            self, store: Store, vote_1: VoteModel
    ):
        vote_id = await store.words.delete_vote(vote_1.id)
        assert vote_id == vote_1.id
        # game = await store.words.get_game_by_id(vote_id.id)
        # assert game is None




