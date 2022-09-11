from hashlib import sha256

from sqlalchemy import select

from app.admin.models import AdminModel
from app.store import Store
from tests.utils import ok_response


class TestAdminStore:
    async def test_create_admin(self, cli, store: Store):
        email = "admin2@admin.com"
        password = "admin2"
        "a4316e43-8052-48d2-8941-96343cac2c8e"
        admin = await store.admins.create_admin(email, password)
        assert type(admin) is AdminModel

        async with cli.app.database.session() as session:
            res = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            user = res.scalar()

        assert user.email == email
        assert user.password == str(
            sha256(password.encode("utf-8")).hexdigest()
        )


class TestAdminLoginView:
    async def test_create_on_startup(self, store: Store, config):
        print(config.admin.email)
        admin = await store.admins.get_by_email(config.admin.email)
        assert admin is not None
        assert admin.email == config.admin.email
        # Password must be hashed
        assert admin.password != config.admin.password
        # id must be uuid
        assert admin.id != 1

    async def test_success(self, cli, config):
        resp = await cli.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["email"] == config.admin.email

    async def test_missed_email(self, cli):
        resp = await cli.post(
            "/admin.login",
            json={
                "password": "qwerty",
            },
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["email"][0] == "Missing data for required field."

    async def test_not_valid_credentials(self, cli):
        resp = await cli.post(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert resp.status == 403
        data = await resp.json()
        assert data["status"] == "forbidden"

    async def test_different_method(self, cli):
        resp = await cli.get(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestAdminCurrentView:
    async def test_unauthorized(self, cli):
        resp = await cli.get(
            "/admin.current",
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success_current_user(self, authed_cli, config):
        resp = await authed_cli.get(
            "/admin.current",
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data["data"]["email"] == config.admin.email
