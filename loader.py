import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
