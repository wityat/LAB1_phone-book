from typing import Dict

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State

from . import texts, keyboards
from ...db.models import *
from ...load_all import dp
from ...modules.api import API
from ...modules.filters import IsUserSubscriber

