import asyncio
import logging

import sqlalchemy
from sqlalchemy import update
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from requests import Session, Request
from db.database import Session as DbSession
from db.database import create_db
from db.models import Car
from mailing import mailing, scrap_auction

ua = UserAgent()
car_list = []
URL = r"https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&categories.main.id=1&brand.id[0]=79&model.id[0]=2104&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page=%s&size=100"
# DAY_OFFER_URL = r"https://auto.ria.com/uk/demo/bu/searchPage/informer/offerOfTheDayV3/?t=/searchPage/informers/offerOfTheDayV3&indexName=auto,order_auto,newauto_search&category_id=1&marka_id[0]=79&model_id[0]=2104&abroad=2&custom=1&langId=4&_mark=1"
# URL_BIDFAX = r"https://en.bidfax.info/?do=search&subaction=search&story="

async def get_autoria_id(url: str) -> str:
    last_underline = url.rfind("_")
    last_dot = url.rfind(".")

    return url[last_underline + 1:last_dot]



async def scrap_cars_page():
    user_agent = {'User-Agent': ua.random}
    db_session = DbSession()

    page_num = 0
    car_nums = -1
    with requests.session() as session:
        while car_nums != 0:
            response = session.get(URL % str(page_num), headers=user_agent)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                car_soup_list = soup.find_all(class_="ticket-item")
                car_nums = len(car_soup_list)

                if car_nums != 0:
                    page_num += 1
                    for car in car_soup_list:
                        child = car.find('a')
                        autoria_link = child.get('href')
                        autoria_id: str = await get_autoria_id(child.get('href'))

                        # some elements like day proposals has js code, try to avoid them
                        if "javascript" in autoria_id:
                            logging.error('JS element error')
                            continue

                        prices = car.find(class_="price-ticket")
                        price_usd: int = int(prices.get('data-main-price'))
                        price_uah: str = car.find(attrs={'data-currency': 'UAH'}).text.replace(' ', '')
                        city: str = car.find('i', class_='icon-location').next_sibling.text.strip()
                        mileage: str = car.find('i', class_="icon-mileage").next_sibling.text.strip()
                        akp: str = car.find('i', class_="icon-akp").next_sibling.text.strip()
                        name_with_year: str = car.find('a', class_="address").text.strip()
                        name, year = name_with_year.split('  ')
                        vin_num: str = car.find('span', class_="label-vin").find('span').text.strip()

                        # auction api
                        # auction_url: str = await scrap_auction(vin_num)

                        car_record = Car(vin_num=vin_num, ria_id=autoria_id, ria_link=autoria_link, year=int(year),
                                         name=name, price_uah=price_uah, price_usd=price_usd,
                                         is_sended=False, city=city, mileage=mileage, akp=akp)

                        old_record = db_session.query(Car).filter(Car.ria_id == autoria_id).first()
                        if old_record is None:
                            logging.info("Found new cars!")
                            db_session.add(car_record)
                            await mailing('new_car', car_record)
                        else:
                            if old_record.price_usd != price_usd:
                                if old_record.price_usd > price_usd:
                                    await mailing(message_type='price_changed', old_car=old_record, car=car_record)
                                    logging.info('Found cheaper price')
                                elif old_record.price_usd < price_usd:
                                    await mailing(message_type='price_changed', old_car=old_record, car=car_record)
                                    logging.info('Seller wanna scam you, price higher')

                                update_price = update(Car).where(Car.ria_id == autoria_id).values(
                                    price_usd=price_usd, price_uah=price_uah, prev_price=old_record.price_usd)
                                db_session.execute(update_price)

                    db_session.commit()
            else:
                print("Failed to retrieve the web page. Status code:", response.status_code)
