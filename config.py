from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BadRequest
from aiogram.utils import exceptions
from loguru import logger
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from emoji import emojize
import pandas as pd

from model import *
import pytz

tz = pytz.timezone('Europe/Moscow')


TOKEN = '5590505820:AAHdJNYfpJGiAmOfh8SRbFdpDWK9VdjDCZE' # тест
# TOKEN = '5802077316:AAGU7w5zuLeC8ZvK5IRaglC6sgci_UnkI2o' # PlanTaskBot



session = Session()

logger.add("file_{time}.log", format="{time} - {level} - {message}", level="TRACE", rotation="7 day")


bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
