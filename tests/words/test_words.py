from dataclasses import asdict

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.words.models import WordModel
from app.store import Store
from tests.utils import check_empty_table_exists
from tests.utils import ok_response


class TestWordStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "words")

    async def test_create_word(self, cli, store: Store, clear_words):
        word_title = "test_word"
        word_is_correct = True
        word = await store.words.create_word(word_title, word_is_correct)
        assert type(word) is WordModel

        async with cli.app.database.session() as session:
            res = await session.execute(select(WordModel))
            words = res.scalars().all()

        assert len(words) == 1
        async with cli.app.database.session() as session:
            res = await session.execute(select(WordModel).where(WordModel.title == word_title))
            new_word = res.scalar()
        assert new_word.title == word_title
        assert new_word.is_correct == word_is_correct

    async def test_create_setting_unique_title_constraint(
        self, store: Store, word_1: WordModel
    ):
        with pytest.raises(IntegrityError) as exc_info:
            await store.words.create_word(word_1.title, word_1.is_correct)
        assert exc_info.value.orig.pgcode == "23505"

    async def test_get_word_by_id(self, store: Store, word_1: WordModel):
        theme = await store.words.get_word_by_id(word_1.id)
        assert theme == word_1

    async def test_get_word_by_title(self, store: Store, word_1: WordModel):
        theme = await store.words.get_word_by_title(word_1.title)
        assert theme == word_1

    async def test_list_words(
        self,
        cli,
        store: Store,
        clear_words,
        word_1: WordModel,
        word_2: WordModel,
    ):
        words = await store.words.list_words()
        assert words == [word_1, word_2]
        words = await store.words.list_words(True)
        assert words == [word_1, ]
        words = await store.words.list_words(False)
        assert words == [word_2, ]

    async def test_delete_word_by_id(self, store: Store, word_1: WordModel):
        word_id = await store.words.delete_word(word_1.id)
        assert word_id == word_1.id
        word = await store.words.get_word_by_id(word_1.id)
        assert word is None

    async def test_patch_word_by_id(self, cli, store: Store, word_1: WordModel, word_2: WordModel):
        word_1_updated = await store.words.patch_word(word_1.id, title="измененноеслово", is_correct=word_2.is_correct)
        assert word_1_updated.is_correct == word_2.is_correct
        assert word_1_updated.title == "измененноеслово"
        assert word_1_updated.id == word_1.id

    async def test_patch_title(self, cli, store: Store, word_1: WordModel):
        word_1_updated = await store.words.patch_word(word_1.id, title="измененноеслово")
        assert word_1_updated.is_correct == word_1.is_correct
        assert word_1_updated.title == "измененноеслово"
        assert word_1_updated.id == word_1.id

    async def test_patch_is_correct(self, cli, store: Store, word_1: WordModel, word_2: WordModel):
        word_1_updated = await store.words.patch_word(word_1.id, is_correct=word_2.is_correct)
        assert word_1_updated.is_correct == word_2.is_correct
        assert word_1_updated.title == word_1.title
        assert word_1_updated.id == word_1.id


class TestWordAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.add_word",
            json={
                "title": "словонеавторизовано",
                "is_correct": True
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli):
        words_before = await store.words.list_words()
        resp = await authed_cli.post(
            "/words.add_word",
            json={
                "title": "словоавторизовано",
                "is_correct": True
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"id": data["data"]["id"], "title": "словоавторизовано", "is_correct": True},
        )
        word_by_id = await store.words.get_word_by_id(data["data"]["id"])
        assert word_by_id is not None
        word_by_title = await store.words.get_word_by_title(
            "словоавторизовано"
        )
        assert word_by_title is not None

        assert word_by_id.id == word_by_title.id
        assert word_by_id.title == word_by_title.title
        assert word_by_id.is_correct == word_by_title.is_correct

        words = await store.words.list_words()
        assert len(words) == len(words_before) + 1

    async def test_missing_title(self, authed_cli):
        resp = await authed_cli.post("/words.add_word", json={"is_correct": True})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["title"][0] == "Missing data for required field."

    async def test_missing_is_correct(self, authed_cli):
        resp = await authed_cli.post("/words.add_word", json={"title": "нетизкоррект"})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["is_correct"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/words.add_word", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    async def test_conflict(self, authed_cli, word_1: WordModel):
        resp = await authed_cli.post(
            "/words.add_word",
            json={
                "title": word_1.title,
                "is_correct": word_1.is_correct
            },
        )
        assert resp.status == 409
        data = await resp.json()
        assert data["status"] == "conflict"


class TestWordsListView:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/words.list_words")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli, clear_words):
        resp = await authed_cli.get("/words.list_words")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"words": []})

    async def test_one(self, authed_cli, clear_words, word_1: WordModel):
        resp = await authed_cli.get("/words.list_words")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"words": [asdict(word_1)]})

    async def test_several(self, authed_cli, clear_words, word_1: WordModel, word_2: WordModel):
        resp = await authed_cli.get("/words.list_words")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"words": [asdict(word_1), asdict(word_2)]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/words.list_words")
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli, clear_words):
        resp = await authed_cli.post(
            "/words.add_word",
            json={
                "title": "тестинтеграция",
                "is_correct": True
            },
        )
        assert resp.status == 200
        data = await resp.json()
        word_id = data["data"]["id"]

        resp = await authed_cli.get("/words.list_words")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "words": [
                    asdict(WordModel(id=word_id, title="тестинтеграция", is_correct=True))
                ]
            }
        )


class TestWordsPatchView:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/words.patch_word")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, authed_cli, clear_words, word_1: WordModel):
        resp = await authed_cli.post(
            "/words.patch_word",
            json={
                "id": word_1.id,
                "title": "измененноеслово",
                "is_correct": True
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={
                "id": word_1.id,
                "title": "измененноеслово",
                "is_correct": True
            }
        )

    async def test_not_found(self, authed_cli, clear_words):
        resp = await authed_cli.post(
            "/words.patch_word",
            json={
                "id": 1,
                "title": "измененноеслово",
                "is_correct": True
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestWordsDeleteView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/words.delete_word",
            json={
                "id": 1
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, authed_cli, clear_words, word_1: WordModel):
        resp = await authed_cli.post(
            "/words.delete_word",
            json={
                "id": word_1.id,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(word_1))

    async def test_not_found(self, authed_cli, clear_words):
        resp = await authed_cli.post(
            "/words.delete_word",
            json={
                "id": 1,
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"


class TestWordsGetView:
    async def test_unauthorized(self, cli):
        resp = await cli.get(
            "/words.get_word",
            params={
                "title": "тест",
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, authed_cli, clear_words, word_1: WordModel):
        resp = await authed_cli.get(
            "/words.get_word",
            params={
                "title": word_1.title,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data=asdict(word_1))

    async def test_not_found(self, authed_cli, clear_words):
        resp = await authed_cli.get(
            "/words.get_word",
            params={
                "title": "тест",
            },
        )
        assert resp.status == 404
        data = await resp.json()
        assert data["status"] == "not_found"
