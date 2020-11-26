from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import get_start_link

from ...db.models import BotUser, Group
from ...load_all import dp, bot
from . import texts, keyboards
from ...modules.api import API, BadResponseStatus
from ...modules.filters import Button, IsBotNewChatMember, IsItNotGroup
from tortoise.query_utils import Q

pass