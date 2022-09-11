from marshmallow import Schema, fields, validates_schema, ValidationError, validate


class WordSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class WordListSchema(Schema):
    words = fields.Nested(WordSchema, many=True)


class WordIsCorrectSchema(Schema):
    is_correct = fields.Bool(required=False)


class WordIdSchema(Schema):
    id = fields.Int(required=True)


class WordTitleSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1), required=True)


class PatchWordSchema(WordIdSchema):
    title = fields.Str(required=False)
    is_correct = fields.Bool(required=False)

    @validates_schema
    def validate_update(self, data, **kwargs):
        title = data.get("title", None)
        is_correct = data.get("is_correct", None)
        if title is None and is_correct is None:
            raise ValidationError("at least one field must be updated")


class SettingSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    timeout = fields.Int(required=True)


class SettingIdSchema(Schema):
    id = fields.Int(required=True)


class PatchSettingSchema(SettingIdSchema):
    title = fields.Str(required=False)
    timeout = fields.Int(required=False)

    @validates_schema
    def validate_update(self, data, **kwargs):
        title = data.get("title", None)
        timeout = data.get("timeout", None)
        if title is None and timeout is None:
            raise ValidationError("at least one field must be updated")


class SettingListSchema(Schema):
    settings = fields.Nested(SettingSchema, many=True)


class SettingTitleSchema(Schema):
    title = fields.Str(required=True)
