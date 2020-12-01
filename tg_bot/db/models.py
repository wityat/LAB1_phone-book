from tortoise.models import Model
from tortoise import fields
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
    first_name = fields.CharField(max_length=255, default="")
    last_name = fields.CharField(max_length=255, default="")
    hash_name = fields.CharField(max_length=64, pk=True)
    phone = fields.CharField(max_length=11, default="")
    birth_day = fields.DateField(null=True)

    def validate_phone(self):
        if self.phone.startswith("+7"):
            self.phone.replace("+7", "8")
        try:
            self.phone = re.match(r"[\d]+", self.phone).group()
        except AttributeError:
            raise ValidateError(exceptions_texts.numbers_phone())
        if not len(self.phone) == 11:
            raise ValidateError(exceptions_texts.len_phone())

    def validate_names(self):
        import string
        fn = any(x for x in string.punctuation if x in self.first_name)
        ln = any(x for x in string.punctuation if x in self.first_name)
        if not fn or not ln:
            raise ValidateError(exceptions_texts.punctuation_names())
        self.first_name.title()
        self.last_name.title()

    def validate(self):
        self.validate_phone()
        self.validate_names()

    def save(self):
        self.validate()
        self.hash_name = sha256((self.first_name+self.last_name).encode('utf-8')).hexdigest()
        super().save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}\n{self.phone}\n{self.birth_day if self.birth_day else ''}"

# aerich init -t config.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade && 