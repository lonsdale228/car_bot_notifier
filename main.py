import asyncio

from db.database import create_db, Session
from db.models import Car, Picture
from loader import dp, bot


async def main():
    create_db()
    session = Session()
    car_test = Car(vin_num="4T1T11AK6PU801580", price=100, is_sended=False)
    car_test.pictures = [Picture(url="amogus.com"), Picture(url="abebus.ua")]
    session.add(car_test)
    session.commit()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
