from datetime import date
from typing import Optional, Iterable

from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.models import Model
from tortoise import fields, BaseDBAsyncClient
from hashlib import sha256
import re

from tg_bot.db.exceptions import ValidateError
from tg_bot.db import exceptions_texts


class BotUser(Model):
    tg_id = fields.BigIntField(default=0)
    token = fields.CharField(max_length=256, default="")
    lang = fields.CharField(max_length=2, default="ru")

    def __str__(self):
        return self.tg_id


class PhoneBookRow(Model):
    birth_day_ = ""
    first_name = fields.CharField(max_length=255, default="")
    last_name = fields.CharField(max_length=255, default="")
    phone = fields.CharField(max_length=11, default="")
    birth_day = fields.DateField(null=True)
    hash_name = fields.CharField(max_length=64, pk=True)

    def validate_dt(self):
        result = re.findall(r"^[\s]*(\d\d[/.]\d\d[/.]\d\d\d\d)[\s]*$", self.birth_day_)
        if result:
            day, month, year = map(int, result[0].split("/" if "/" in result[0] else "."))
            try:
                d = date(day=day, month=month, year=year)
            except Exception as e:
                raise ValidateError(exceptions_texts.bad_date())
            else:
                self.birth_day = d

    def validate_phone(self):
        if self.phone.startswith("+7"):
            self.phone.replace("+7", "8")
        print(self.phone, flush=True)
        try:
            self.phone = re.match(r"[\d]+", self.phone).group()
        except AttributeError:
            raise ValidateError(exceptions_texts.numbers_phone())
        if not len(self.phone) == 11:
            raise ValidateError(exceptions_texts.len_phone())

    def validate_names(self):
        if not self.first_name or not self.last_name:
            raise ValidateError(exceptions_texts.no_fn_or_ln())
        import string
        fn = any(x for x in string.punctuation if x in self.first_name)
        ln = any(x for x in string.punctuation if x in self.last_name)
        if fn or ln:
            raise ValidateError(exceptions_texts.punctuation_names())
        self.first_name.title()
        self.last_name.title()

    def validate(self):
        self.validate_phone()
        self.validate_names()
        self.validate_dt()

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
        self.validate()
        print(self.birth_day, self.birth_day_, flush=True)
        self.hash_name = sha256((self.first_name+self.last_name).encode('utf-8')).hexdigest()
        await super().save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}\n{self.phone}\n{self.birth_day if self.birth_day else ''}"

# aerich init -t config.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade && 