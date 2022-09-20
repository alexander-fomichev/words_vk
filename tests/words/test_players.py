from dataclasses import asdict
from typing import List

from sqlalchemy.future import select

from app.words.models import GameModel, PlayerModel
from app.store import Store
from tests.utils import check_empty_table_exists
from tests.utils import ok_response


class TestPlayerStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "players")

    async def test_create_player(self, cli, store: Store, clear_games, clear_settings, game_1: GameModel):
        user_id = 1
        user_name = "test"
        player = await store.words.create_player(
            user_id=user_id, game_id=game_1.id, name=user_name
        )
        assert type(player) is PlayerModel

        async with cli.app.database.session() as session:
            res = await session.execute(select(PlayerModel))
            players = res.scalars().all()

        assert len(players) == 1
        async with cli.app.database.session() as session:
            res = await session.execute(
                select(PlayerModel).where(PlayerModel.user_id == user_id and PlayerModel.game_id == game_1.id)
            )
            new_player = res.scalar()
        assert new_player.user_id == user_id
        assert new_player.game_id == game_1.id
        assert new_player.name == user_name
        assert new_player.status == "Active"
        assert new_player.online is True

    async def test_get_player(
        self, store: Store, player_1: PlayerModel
    ):
        player = await store.words.get_player(player_id=player_1.id)
        assert player == player_1

    async def test_list_players(
        self,
        cli,
        store: Store,
        clear_games,
        player_1: PlayerModel,
        player_2: PlayerModel,
    ):
        players = await store.words.list_player(player_1.game_id)
        assert players == [player_1, ]
        players = await store.words.list_player(player_2.game_id)
        assert players == [player_2, ]

    async def test_delete_player(
        self, store: Store, player_1: PlayerModel
    ):
        player_id = await store.words.delete_player(player_1.id)
        assert player_id == player_1.id
        game = await store.words.get_player(player_1.id)
        assert game is None

    async def test_patch_player(
        self,
        cli,
        store: Store,
        player_1: PlayerModel,
    ):
        player_1_updated = await store.words.patch_player(
            player_id=player_1.id, status="Winner", online=False
        )
        assert player_1_updated.status == "Winner"
        assert player_1_updated.user_id == player_1.user_id
        assert player_1_updated.game_id == player_1.game_id
        assert player_1_updated.online is False


class TestPlayerAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.add_player",
            json={"game_id": 1, "user_id": 30, "name": "test"},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli, game_1):
        players_before = await store.words.list_player(game_1.id)
        resp = await authed_cli.post(
            "/words.add_player",
            json={"game_id": game_1.id, "user_id": 30, "name": "test"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": data["data"]["id"],
                "game_id": game_1.id,
                "user_id": 30,
                "status": "Active",
                "online": True,
                "name": "test",
                "score": 0
            },
        )
        player = await store.words.get_player(data["data"]["id"])
        assert player is not None

        assert player.game_id == game_1.id
        assert player.user_id == 30
        assert player.online is True
        assert player.status == "Active"
        assert player.name == "test"

        players = await store.words.list_player(game_1.id)
        assert len(players) == len(players_before) + 1

    async def test_missing_game_id(self, authed_cli):
        resp = await authed_cli.post("/words.add_player", json={"user_id": 45, "name": "test"})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["game_id"][0] == "Missing data for required field."

    async def test_missing_user_id(self, authed_cli):
        resp = await authed_cli.post(
            "/words.add_player", json={"game_id": 1, "name": "test"}
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["user_id"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/words.add_player", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    async def test_conflict(self, authed_cli, clear_games, player_1: PlayerModel):
        resp = await authed_cli.post(
            "/words.add_player",
            json={"game_id": player_1.game_id, "user_id": player_1.user_id, "name": "test"},
        )
        assert resp.status == 409
        data = await resp.json()
        assert data["status"] == "conflict"

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.post(
            "/words.add_player",
            json={"game_id": 1, "user_id": 30, "name": "test"},
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestPlayerListView:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/words.list_players", params={"id": 1})
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli, clear_games, game_1: GameModel):
        resp = await authed_cli.get("/words.list_players", params={"id": game_1.id})
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"players": []})

    async def test_one(
        self, authed_cli, clear_games, player_1: PlayerModel
    ):
        resp = await authed_cli.get("/words.list_players", params={"id": player_1.game_id})
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"players": [asdict(player_1)]})

    async def test_several(
        self,
        authed_cli,
        clear_games,
        player_3_4: List[GameModel]
    ):
        resp = await authed_cli.get("/words.list_players", params={"id": player_3_4[0].game_id})
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"players": [asdict(player_3_4[0]), asdict(player_3_4[1])]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/words.list_players", params={"id": 1})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli, clear_games, game_1: GameModel):
        resp = await authed_cli.post(
            "/words.add_player",
            json={"game_id": game_1.id, "user_id": 30, "name": "test"},
        )
        assert resp.status == 200
        data = await resp.json()
        player_id = data["data"]["id"]

        resp = await authed_cli.get("/words.list_players", params={"id": game_1.id})
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "players": [
                    asdict(
                        PlayerModel(
                            id=player_id, user_id=30, game_id=game_1.id, name="test", status="Active", online=True, score=0
                        )
                    )
                ]
            }
        )


class TestPlayerPatchView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.patch_player",
            json={"id": 1, "status": "Winner"},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_games, player_1: PlayerModel
    ):
        resp = await authed_cli.post(
            "/words.patch_player",
            json={"id": player_1.id, "status": "Winner"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": player_1.id,
                "status": "Winner",
                "game_id": player_1.game_id,
                "user_id": player_1.user_id,
                "online": player_1.online,
                "name": player_1.name,
                "score": 0,
            }
        )

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.post(
            "/words.patch_player",
            json={"id": 1, "status": "Winner"},
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestPlayerDeleteView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.delete_player",
            json={"id": 1},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_games, player_1: PlayerModel
    ):
        resp = await authed_cli.post(
            "/words.delete_player",
            json={
                "id": player_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(player_1))

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.post(
            "/words.delete_player",
            json={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestPlayerGetView:
    async def test_unauthorized(self, cli):
        resp = await cli.get(
            "/words.get_player",
            params={
                "id": 1,
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_games, player_1: PlayerModel
    ):
        resp = await authed_cli.get(
            "/words.get_player",
            params={
                "id": player_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(player_1))

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.get(
            "/words.get_player",
            params={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"
