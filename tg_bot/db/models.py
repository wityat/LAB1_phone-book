from datetime import datetime
from typing import Optional, Iterable

from tortoise.exceptions import DoesNotExist, OperationalError, IntegrityError
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
            return await (super().get(**kwargs))
        except DoesNotExist:
            raise ValidateError(exceptions_texts.does_not_exist())
        except ValueError:
            raise ValidateError(exceptions_texts.no_fn_or_ln() + "\n\n" + exceptions_texts.no_phone())

    @classmethod
    async def get_with_check_bd(cls, **kwargs):
        row = await cls.get_(**kwargs)
        if row.birth_day:
            return row
        else:
            raise ValidateError(exceptions_texts.no_bd())

    @classmethod
    async def create_(cls, **kwargs):
        try:
            return await (super().create(**kwargs))
        except DoesNotExist:
            raise ValidateError(exceptions_texts.does_not_exist())
        except ValueError:
            raise ValidateError(exceptions_texts.no_fn_or_ln() + "\n\n" + exceptions_texts.no_phone())

    async def save(
            self,
            using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[Iterable[str]] = None,
            force_create: bool = False,
            force_update: bool = False,
    ) -> None:
        print(self.first_name, self.last_name, self.phone, self.birth_day, type(self.birth_day), flush=True)
        self.first_name, self.last_name, \
        self.phone, self.birth_day = validate_all(self.first_name, self.last_name,
                                                  self.phone, self.birth_day).values()
        print(self.first_name, self.last_name, self.phone, self.birth_day, type(self.birth_day), flush=True)
        self.hash_name = sha256((self.first_name + self.last_name).encode('utf-8')).hexdigest()
        try:
            await (super().save(using_db, update_fields, force_create, force_update))
        except IntegrityError:
            raise ValidateError(exceptions_texts.fn_and_ln_not_unique())

    def __str__(self):
        return f"{self.first_name} {self.last_name}\n{self.phone}\n{self.birth_day if self.birth_day else ''}"

# aerich init -t config.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade &&
