import asyncio

from db.database import create_db, Session
from db.models import Car, Picture
from loader import dp, bot


async def main():
    create_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
