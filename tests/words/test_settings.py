from dataclasses import asdict

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.words.models import SettingModel
from app.store import Store
from tests.utils import check_empty_table_exists
from tests.utils import ok_response


class TestSettingStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "settings")

    async def test_create_setting(self, cli, store: Store, clear_settings):
        setting_title = "test_setting"
        setting_timeout = 30
        setting = await store.words.create_setting(
            setting_title, setting_timeout
        )
        assert type(setting) is SettingModel

        async with cli.app.database.session() as session:
            res = await session.execute(select(SettingModel))
            settings = res.scalars().all()

        assert len(settings) == 1
        async with cli.app.database.session() as session:
            res = await session.execute(
                select(SettingModel).where(SettingModel.title == setting_title)
            )
            new_setting = res.scalar()
        assert new_setting.title == setting_title
        assert new_setting.timeout == setting_timeout

    async def test_create_setting_unique_title_constraint(
        self, store: Store, setting_1: SettingModel
    ):
        with pytest.raises(IntegrityError) as exc_info:
            await store.words.create_setting(setting_1.title, setting_1.timeout)
        assert exc_info.value.orig.pgcode == "23505"

    async def test_get_setting_by_id(
        self, store: Store, setting_1: SettingModel
    ):
        setting = await store.words.get_setting_by_id(setting_1.id)
        assert setting == setting_1

    async def test_get_setting_by_title(
        self, store: Store, setting_1: SettingModel
    ):
        setting = await store.words.get_setting_by_title(setting_1.title)
        assert setting == setting_1

    async def test_list_settings(
        self,
        cli,
        store: Store,
        clear_settings,
        setting_1: SettingModel,
        setting_2: SettingModel,
    ):
        settings = await store.words.list_settings()
        assert settings == [setting_1, setting_2]

    async def test_delete_setting_by_id(
        self, store: Store, setting_1: SettingModel
    ):
        setting_id = await store.words.delete_setting(setting_1.id)
        assert setting_id == setting_1.id
        setting = await store.words.get_setting_by_id(setting_1.id)
        assert setting is None

    async def test_patch_setting_by_id(
        self,
        cli,
        store: Store,
        setting_1: SettingModel,
        setting_2: SettingModel,
    ):
        setting_1_updated = await store.words.patch_setting(
            setting_1.id, title="измененнаянастройка", timeout=setting_2.timeout
        )
        assert setting_1_updated.timeout == setting_2.timeout
        assert setting_1_updated.title == "измененнаянастройка"
        assert setting_1_updated.id == setting_1.id

    async def test_patch_title(
        self, cli, store: Store, setting_1: SettingModel
    ):
        setting_1_updated = await store.words.patch_setting(
            setting_1.id, title="измененнаянастройка"
        )
        assert setting_1_updated.timeout == setting_1.timeout
        assert setting_1_updated.title == "измененнаянастройка"
        assert setting_1_updated.id == setting_1.id


class TestSettingAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.add_setting",
            json={"title": "настройканеавторизовано", "timeout": 30},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli):
        settings_before = await store.words.list_settings()
        resp = await authed_cli.post(
            "/words.add_setting",
            json={"title": "настройкаавторизовано", "timeout": 45},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": data["data"]["id"],
                "title": "настройкаавторизовано",
                "timeout": 45,
            },
        )
        setting_by_id = await store.words.get_setting_by_id(data["data"]["id"])
        assert setting_by_id is not None
        setting_by_title = await store.words.get_setting_by_title(
            "настройкаавторизовано"
        )
        assert setting_by_title is not None

        assert setting_by_id.id == setting_by_title.id
        assert setting_by_id.title == setting_by_title.title
        assert setting_by_id.timeout == setting_by_title.timeout

        settings = await store.words.list_settings()
        assert len(settings) == len(settings_before) + 1

    async def test_missing_title(self, authed_cli):
        resp = await authed_cli.post("/words.add_setting", json={"timeout": 45})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["title"][0] == "Missing data for required field."

    async def test_missing_timeout(self, authed_cli):
        resp = await authed_cli.post(
            "/words.add_setting", json={"title": "нетаймаута"}
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["timeout"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/words.add_setting", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    async def test_conflict(self, authed_cli, setting_1: SettingModel):
        resp = await authed_cli.post(
            "/words.add_setting",
            json={"title": setting_1.title, "timeout": setting_1.timeout},
        )
        assert resp.status == 409
        data = await resp.json()
        assert data["status"] == "conflict"


class TestSettingsListView:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/words.list_settings")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli, clear_settings):
        resp = await authed_cli.get("/words.list_settings")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"settings": []})

    async def test_one(
        self, authed_cli, clear_settings, setting_1: SettingModel
    ):
        resp = await authed_cli.get("/words.list_settings")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"settings": [asdict(setting_1)]})

    async def test_several(
        self,
        authed_cli,
        clear_settings,
        setting_1: SettingModel,
        setting_2: SettingModel,
    ):
        resp = await authed_cli.get("/words.list_settings")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"settings": [asdict(setting_1), asdict(setting_2)]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/words.list_settings")
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli, clear_settings):
        resp = await authed_cli.post(
            "/words.add_setting",
            json={"title": "тестинтеграция", "timeout": 45},
        )
        assert resp.status == 200
        data = await resp.json()
        setting_id = data["data"]["id"]

        resp = await authed_cli.get("/words.list_settings")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "settings": [
                    asdict(
                        SettingModel(
                            id=setting_id, title="тестинтеграция", timeout=45
                        )
                    )
                ]
            }
        )


class TestSettingsPatchView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.patch_setting",
            json={"id": 1, "title": "измененноеслово", "timeout": 120},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_settings, setting_1: SettingModel
    ):
        resp = await authed_cli.post(
            "/words.patch_setting",
            json={
                "id": setting_1.id,
                "title": "измененноеслово",
                "timeout": 120,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "id": setting_1.id,
                "title": "измененноеслово",
                "timeout": 120,
            }
        )

    async def test_not_found(self, authed_cli, clear_settings):
        resp = await authed_cli.post(
            "/words.patch_setting",
            json={"id": 1, "title": "измененноеслово", "timeout": 45},
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestSettingsDeleteView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.delete_setting",
            json={"id": 1},
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_settings, setting_1: SettingModel
    ):
        resp = await authed_cli.post(
            "/words.delete_setting",
            json={
                "id": setting_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(setting_1))

    async def test_not_found(self, authed_cli, clear_settings):
        resp = await authed_cli.post(
            "/words.delete_setting",
            json={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestSettingsGetView:
    async def test_unauthorized(self, cli):
        resp = await cli.get(
            "/words.get_setting",
            params={
                "title": "тест",
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(
        self, authed_cli, clear_settings, setting_1: SettingModel
    ):
        resp = await authed_cli.get(
            "/words.get_setting",
            params={
                "title": setting_1.title,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(setting_1))

    async def test_not_found(self, authed_cli, clear_settings):
        resp = await authed_cli.get(
            "/words.get_setting",
            params={
                "title": "тест",
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"
