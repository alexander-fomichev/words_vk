from marshmallow import Schema, fields, validates, ValidationError


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested("AnswerSchema", many=True, required=True)

    @validates("answers")
    def validate_answers(self, value):
        if len(value) < 2:
            raise ValidationError("At least two answers required")
        if len(tuple(filter(lambda x: x["is_correct"], value))) != 1:
            raise ValidationError("Exactly one correct answer required")


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int()


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)
