from datetime import date
from typing import Optional, Iterable

from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.models import Model
from tortoise import fields, BaseDBAsyncClient
from hashlib import sha256
import re

from tg_bot.db.exceptions import ValidateError
from tg_bot.db import exceptions_texts
from tg_bot.modules.validation import validate_all


class BotUser(Model):
    tg_id = fields.BigIntField(default=0)
    token = fields.CharField(max_length=256, default="")
    lang = fields.CharField(max_length=2, default="ru")

    def __str__(self):
        return self.tg_id


class PhoneBookRow(Model):
    first_name = fields.CharField(max_length=255, default="")
    last_name = fields.CharField(max_length=255, default="")
    phone = fields.CharField(max_length=11, default="")
    birth_day = fields.DateField(null=True)
    hash_name = fields.CharField(max_length=64, pk=True)

    @classmethod
    async def get_(cls, **kwargs):
        try:
            return await cls.get(**kwargs)
        except DoesNotExist:
            raise ValidateError(exceptions_texts.does_not_exist())

    @classmethod
    async def delete_(cls, **kwargs):
        try:
            await cls.delete(**kwargs)
        except OperationalError:
            raise ValidateError(exceptions_texts.does_not_exist())

    async def save(
            self,
            using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[Iterable[str]] = None,
            force_create: bool = False,
            force_update: bool = False,
    ) -> None:
        self.first_name, self.last_name, \
        self.phone, self.birth_day = validate_all(self.first_name, self.last_name,
                                                  self.phone, self.birth_day).values()
        self.hash_name = sha256((self.first_name + self.last_name).encode('utf-8')).hexdigest()
        await super().save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}\n{self.phone}\n{self.birth_day if self.birth_day else ''}"

# aerich init -t config.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade &&
