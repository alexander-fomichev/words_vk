from marshmallow import Schema, fields


class AdminSchema(Schema):
    id = fields.UUID(required=False)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
