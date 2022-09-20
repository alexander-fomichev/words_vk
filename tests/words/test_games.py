from dataclasses import asdict

from sqlalchemy import delete
from sqlalchemy.future import select

from app.words.models import SettingModel, GameModel, PlayerModel
from app.store import Store
from tests.utils import check_empty_table_exists
from tests.utils import ok_response


class TestGameStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "games")

    async def test_create_game(self, cli, store: Store, clear_games, clear_settings, setting_1: SettingModel):
        peer_id = 1
        game = await store.words.create_game(
            setting_id=setting_1.id,
            peer_id=peer_id
        )
        assert type(game) is GameModel

        async with cli.app.database.session() as session:
            res = await session.execute(select(GameModel))
            games = res.scalars().all()

        assert len(games) == 1
        async with cli.app.database.session() as session:
            res = await session.execute(
                select(GameModel).where(GameModel.peer_id == peer_id)
            )
            new_game = res.scalar()
        assert new_game.peer_id == peer_id
        assert new_game.setting_id == setting_1.id
        assert new_game.status == "init"

    async def test_get_game_by_id(
            self, store: Store, game_1: GameModel
    ):
        game = await store.words.get_game_by_id(game_1.id)
        assert game == game_1

    async def test_list_games(
            self,
            cli,
            store: Store,
            clear_settings,
            clear_games,
            game_1: GameModel,
            game_2: GameModel,
    ):
        games = await store.words.list_games()
        assert len(games) == 2
        assert game_1 in games
        assert game_2 in games
        games = await store.words.list_games(game_1.peer_id)
        assert games == [game_1, ]

    async def test_delete_game(
            self, store: Store, game_1: GameModel
    ):
        game_id = await store.words.delete_game(game_1.id)
        assert game_id == game_1.id
        game = await store.words.get_game_by_id(game_1.id)
        assert game is None

    async def test_patch_game(
            self,
            cli,
            store: Store,
            game_1: GameModel,
    ):
        game_1_updated = await store.words.patch_game(
            game_1.id, status="Finished"
        )
        assert game_1_updated.status == "Finished"
        assert game_1_updated.id == game_1.id
        assert game_1_updated.players == game_1.players


    async def test_check_cascade_delete(
            self, cli, player_1: PlayerModel
    ):
        async with cli.app.database.session() as session:
            await session.execute(delete(GameModel).where(GameModel.id == player_1.game_id))
            await session.commit()

            res = await session.execute(
                select(PlayerModel).where(
                    PlayerModel.game_id == player_1.game_id and PlayerModel.user_id == player_1.user_id
                )
            )
            players = res.scalars().all()

        assert len(players) == 0


class TestGameAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.add_game",
            json={
                "setting_id": "197",
                "peer_id": 45
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli, setting_1):
        games_before = await store.words.list_games()
        resp = await authed_cli.post(
            "/words.add_game",
            json={
                "setting_id": setting_1.id,
                "peer_id": 45
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": data["data"]["id"],
                "players": [],
                "setting": asdict(setting_1),
                "peer_id": 45,
                "status": "init",
                "moves_order": None,
                "event_timestamp": None,
                "elapsed_time": 0,
                "current_move": None,
                "last_word": None,
                "vote_word": None,
            },
        )
        game = await store.words.get_game_by_id(data["data"]["id"])
        assert game is not None

        assert game.id == data["data"]["id"]
        assert game.players == []
        assert game.setting_id == setting_1.id
        assert game.peer_id == 45
        assert game.status == "init"

        games = await store.words.list_games()
        assert len(games) == len(games_before) + 1

    async def test_missing_setting_id(self, authed_cli):
        resp = await authed_cli.post("/words.add_game", json={"peer_id": 45})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["setting_id"][0] == "Missing data for required field."

    async def test_missing_peer_id(self, authed_cli):
        resp = await authed_cli.post(
            "/words.add_game", json={"setting_id": "нетаймаута"}
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["peer_id"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/words.add_game", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    # async def test_conflict(self, authed_cli, setting_1: SettingModel):
    #     resp = await authed_cli.post(
    #         "/words.add_game",
    #         json={"title": setting_1.title, "timeout": setting_1.timeout},
    #     )
    #     assert resp.status == 409
    #     data = await resp.json()
    #     assert data["status"] == "conflict"


class TestGamesListView:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/words.list_games")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli, clear_games):
        resp = await authed_cli.get("/words.list_games")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"games": []})

    async def test_one(
            self, authed_cli, clear_games, game_1: GameModel
    ):
        resp = await authed_cli.get("/words.list_games")
        assert resp.status == 200
        data = await resp.json()
        test_1 = asdict(game_1)
        test_1.pop("setting_id")
        assert data == ok_response(data={"games": [test_1, ]})

    async def test_several(
            self,
            authed_cli,
            clear_games,
            game_1: GameModel,
            game_2: GameModel,
    ):
        resp = await authed_cli.get("/words.list_games")
        assert resp.status == 200
        data = await resp.json()
        test_1 = asdict(game_1)
        test_1.pop("setting_id")
        test_2 = asdict(game_2)
        test_2.pop("setting_id")
        assert data == ok_response(
            data={"games": [test_2, test_1, ]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/words.list_games")
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli, clear_games, setting_1: SettingModel):
        resp = await authed_cli.post(
            "/words.add_game",
            json={
                "setting_id": setting_1.id,
                "peer_id": 45
            }
        )
        assert resp.status == 200
        data = await resp.json()
        game_id = data["data"]["id"]

        resp = await authed_cli.get("/words.list_games")
        assert resp.status == 200
        data = await resp.json()
        game = asdict(
            GameModel(
                id=game_id,
                status="init",
                setting_id=setting_1.id,
                players=[],
                peer_id=45,
                moves_order=None,
                current_move=None,
                event_timestamp=None,
                elapsed_time=0,
                last_word=None,
                vote_word=None
            )
        )
        game.pop("setting_id")
        game["setting"] = asdict(setting_1)

        assert data == ok_response(
            data={
                "games": [
                    game
                ]
            }
        )


class TestGamePatchView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.patch_game",
            json={
                "id": 1,
                "status": "finished",
            }
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
            self, authed_cli, clear_games, game_1: GameModel
    ):
        resp = await authed_cli.post(
            "/words.patch_game",
            json={
                "id": game_1.id,
                "status": "finished",
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": game_1.id,
                "status": "finished",
                "setting": asdict(game_1.setting),
                "players": [],
                "peer_id": game_1.peer_id,
                "moves_order": None,
                "current_move": None,
                "event_timestamp": None,
                "elapsed_time": 0,
                "last_word": None,
                "vote_word": None,
            }
        )

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.post(
            "/words.patch_game",
            json={
                "id": 1,
                "status": "finished",
            }
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestGameDeleteView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.delete_game",
            json={"id": 1},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
            self, authed_cli, clear_settings, clear_games, game_1: GameModel
    ):
        resp = await authed_cli.post(
            "/words.delete_game",
            json={
                "id": game_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        test_1 = asdict(game_1)
        test_1.pop("setting_id")
        assert data == ok_response(data=test_1)

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.post(
            "/words.delete_game",
            json={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestGameGetView:
    async def test_unauthorized(self, cli):
        resp = await cli.get(
            "/words.get_game",
            params={
                "id": 1,
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
            self, authed_cli, clear_games, game_1: GameModel
    ):
        resp = await authed_cli.get(
            "/words.get_game",
            params={
                "id": game_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        test_1 = asdict(game_1)
        test_1.pop("setting_id")
        assert data == ok_response(data=test_1)

    async def test_not_found(self, authed_cli, clear_games):
        resp = await authed_cli.get(
            "/words.get_game",
            params={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"
