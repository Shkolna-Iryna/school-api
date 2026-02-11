import re
from marshmallow import Schema, fields, validate

REGEXP_EMAIL = re.compile(r"^[\w.-]+@[\w.-]+\.\w{2,6}$")


class LoginSchema(Schema):
    email = fields.String(
        required=True,
        error_messages={
            "required": "Поле є обов'язковим",
            "null": "Поле є обов'язковим",
        },
        validate=validate.Regexp(REGEXP_EMAIL, error="Неправильний формати пошти"),
    )

    password = fields.String(
        required=True,
        error_messages={
            "required": "Поле є обов'язковим",
            "null": "Поле є обов'язковим",
        },
        validate=validate.Length(min=6, error="Необхідно мінімум шість символів"),
    )


class RegisterSchema(Schema):
    name = fields.String(
        required=True,
        error_messages={
            "required": "Поле є обов'язковим",
            "null": "Поле є обов'язковим",
        },
        validate=validate.Length(min=2, error="Необхідно мінімум два символи"),
    )

    email = fields.String(
        required=True,
        error_messages={
            "required": "Поле є обов'язковим",
            "null": "Поле є обов'язковим",
        },
        validate=validate.Regexp(REGEXP_EMAIL, error="Неправильний формати пошти"),
    )

    password = fields.String(
        required=True,
        error_messages={
            "required": "Поле є обов'язковим",
            "null": "Поле є обов'язковим",
        },
        validate=validate.Length(min=6, error="Необхідно мінімум шість символів"),
    )
