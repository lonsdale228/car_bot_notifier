import asyncio
import sqlalchemy
from sqlalchemy import update
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from requests import Session, Request
from db.database import Session as DbSession
from db.database import create_db
from db.models import Car

ua = UserAgent()
car_list = []
URL = r"https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&categories.main.id=1&brand.id[0]=79&model.id[0]=2104&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page=0&size=100"
DAY_OFFER_URL = r"https://auto.ria.com/uk/demo/bu/searchPage/informer/offerOfTheDayV3/?t=/searchPage/informers/offerOfTheDayV3&indexName=auto,order_auto,newauto_search&category_id=1&marka_id[0]=79&model_id[0]=2104&abroad=2&custom=1&langId=4&_mark=1"


async def get_autoria_id(url: str) -> str:
    last_underline = url.rfind("_")
    last_dot = url.rfind(".")

    return url[last_underline + 1:last_dot]


async def scrap_cars_page(url):
    user_agent = {'User-Agent': ua.random}
    db_session = DbSession()

    with requests.session() as session:
        response = session.get(url, headers=user_agent)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            car_soup_list = soup.find_all(class_="ticket-item")
            for car in car_soup_list:
                child = car.find('a')
                autoria_link = child.get('href')
                autoria_id: str = await get_autoria_id(child.get('href'))
                if "javascript" in autoria_id:
                    continue

                old_record = db_session.query(Car).filter(Car.ria_id == autoria_id).first()

                prices = car.find(class_="price-ticket")
                price_usd: int = int(prices.get('data-main-price'))
                price_uah: str = car.find(attrs={'data-currency': 'UAH'}).text.replace(' ', '')
                vin_num: str = car.find('span', class_="label-vin").find('span').text.strip()

                if old_record is None:
                    car_record = Car(vin_num=vin_num, ria_id=autoria_id, ria_link=autoria_link, price_uah=price_uah,
                                     price_usd=price_usd, is_sended=False)
                    db_session.add(car_record)
                else:
                    if old_record.price_usd > price_usd:
                        update_price = update(Car). \
                            where(Car.ria_id == autoria_id). \
                            values(price_usd=price_usd, price_uah=price_uah, prev_price=old_record.price_usd)
                        db_session.execute(update_price)
                        print("Price cheaper")
                    elif old_record.price_usd < price_usd:
                        update_price = update(Car). \
                            where(Car.ria_id == autoria_id). \
                            values(price_usd=price_usd, price_uah=price_uah, prev_price=old_record.price_usd)
                        db_session.execute(update_price)
                        print("Price more expensive")

            db_session.commit()
        else:
            print("Failed to retrieve the web page. Status code:", response.status_code)


create_db()
asyncio.run(scrap_cars_page(URL))
