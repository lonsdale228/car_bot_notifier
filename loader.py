import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
scheduler = AsyncIOScheduler()
dp = Dispatcher(sheduler=scheduler)

CHANNEL_ID = 317465871
