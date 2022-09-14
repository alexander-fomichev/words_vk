from marshmallow import (
    Schema,
    fields,
    validates_schema,
    ValidationError,
    validate,
)


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


class PlayerSchema(Schema):
    id = fields.Int(required=False)
    status = fields.Str(required=False)
    online = fields.Bool(required=False)
    name = fields.Str(required=False)
    game_id = fields.Int(required=True)
    user_id = fields.Int(required=True)


class PlayerIdSchema(Schema):
    id = fields.Int(required=True)


class PatchPlayerSchema(PlayerIdSchema):
    status = fields.Str(required=False)
    online = fields.Bool(required=False)

    @validates_schema
    def validate_update(self, data, **kwargs):
        status = data.get("status", None)
        online = data.get("online", None)
        if online is None and status is None:
            raise ValidationError("at least one field must be updated")


class PlayerListSchema(Schema):
    players = fields.Nested(PlayerSchema, many=True)


class GameSchema(Schema):
    id = fields.Int(required=False)
    status = fields.Str(required=False)
    players = fields.Nested(PlayerSchema, many=True)
    setting_id = fields.Int(required=True, load_only=True)
    peer_id = fields.Int(required=True)
    current_move = fields.Int(required=False)
    moves_order = fields.Str(required=False)
    event_timestamp = fields.Time(required=False)
    pause_timestamp = fields.Time(required=False)


class GameIdSchema(Schema):
    id = fields.Int(required=True)


class PeerIdSchema(Schema):
    peer_id = fields.Int(required=False)


class GamePatchSchema(GameIdSchema):
    status = fields.Str(required=False)
    players = fields.Nested(PlayerSchema, many=True, required=False)
    current_move = fields.Int(required=False)
    moves_order = fields.Str(required=False)
    event_timestamp = fields.Time(required=False)
    pause_timestamp = fields.Time(required=False)

    @validates_schema
    def validate_update(self, data, **kwargs):
        status = data.get("status", None)
        players = data.get("players", None)
        current_move = data.get("current_move", None)
        moves_order = data.get("moves_order", None)
        event_timestamp = data.get("event_timestamp", None)
        pause_timestamp = data.get("pause_timestamp", None)

        if players is None\
                and status is None \
                and players is None \
                and current_move is None\
                and moves_order is None\
                and event_timestamp is None\
                and pause_timestamp is None:
            raise ValidationError("at least one field must be updated")


class GameSettingSchema(GameSchema):
    setting = fields.Nested(SettingSchema)


class GameListSchema(Schema):
    games = fields.Nested(GameSettingSchema, many=True)
