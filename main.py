import asyncio
from db.database import create_db, engine
from loader import dp, bot, scheduler
from mailing import mailing
from scrapper import scrap_cars_page


async def main():
    create_db()
    await scrap_cars_page()
    scheduler.add_job(mailing, 'interval', minutes=10)
    scheduler.add_job(scrap_cars_page, 'interval', minutes=5)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        scheduler.shutdown()
        bot.session.close()
        engine.dispose()
