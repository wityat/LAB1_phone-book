import asyncio
from tortoise.models import Model
from tortoise import fields
from hashlib import sha256
import re


class BotUser(Model):
    tg_id = fields.BigIntField(default=0)
    token = fields.CharField(max_length=256, default="")
    lang = fields.CharField(max_length=2, default="ru")

    def __str__(self):
        return self.tg_id


class PhoneBook(Model):
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
            pass
        if len(self.phone) == 11:
            return True

    def save(self):
        self.first_name.title()
        self.last_name.title()
        self.hash_name = sha256((self.first_name+self.last_name).encode('utf-8')).hexdigest()
        super().save()

    def __str__(self):
        return self.tg_id

# aerich init -t config.TORTOISE_ORM && aerich init-db && aerich migrate && aerich upgrade && 