from hashlib import sha256

from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session, get_session

from app.admin.models import AdminModel
from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["auth"], summary="Login", description="Login admin user")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]
        user = await self.request.app.store.admins.get_by_email(email)
        if not user or user.password != str(
            sha256(password.encode("utf-8")).hexdigest()
        ):
            raise HTTPForbidden
        else:
            user_out = AdminSchema().dump(user)
            session = await new_session(self.request)
            session["admin"] = user_out
            return json_response(data=user_out)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["auth"], summary="Current user", description="Get current user info")
    @response_schema(AdminSchema, 200)
    async def get(self):
        session = await get_session(self.request)
        user = AdminModel.from_session(session)
        return json_response(data=AdminSchema().dump(user))
