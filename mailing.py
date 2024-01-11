import asyncio
import logging

from aiogram.enums import ParseMode
from aiogram.types import InputMediaPhoto
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from random import shuffle
from db.database import Session as DbSession
from db.models import Car
from sqlalchemy import update
from loader import bot, CHANNEL_ID

ua = UserAgent()

URL_AUCTION = r"https://americamotors.com/api/search/"


async def scrap_auction(vin_num):
    user_agent = {'User-Agent': ua.random}

    response = requests.get(URL_AUCTION + vin_num, headers=user_agent)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['url']
        else:
            return None


async def scrap_images(car_url: str, image_nums=5, random_images=False, better_quality=False) -> list[str]:
    image_urls = []
    user_agent = {'User-Agent': ua.random}

    response = requests.get(car_url, headers=user_agent)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images_container = soup.find('div', attrs={'class': 'wrapper', 'photocontainer': 'photo'})
        image_list_soup = images_container.find_all('img')

        if random_images:
            shuffle(image_list_soup)

        for i in range(image_nums):
            # replaced for better quality
            if better_quality:
                image_urls.append(image_list_soup[i].get('src').replace('s.', 'hd.'))
            else:
                image_urls.append(image_list_soup[i].get('src'))

    else:
        print("Error getting images!")

    return image_urls


is_notif_sended = False


async def mailing(message_type: str = 'mailing', car=None, old_car=None):
    global is_notif_sended



    match message_type:
        case 'mailing':
            session = DbSession()
            car = session.query(Car).filter(Car.is_sended == 0).first()
            if car:
                auction_url: str = await scrap_auction(car.vin_num)
                image_urls = await scrap_images(car.ria_link)
                caption = f'<a href="{car.ria_link}">{car.name}  {car.year}</a> \n' \
                          f'💲{car.price_usd} \n' \
                          f'🇺🇦 {car.price_uah} грн \n' \
                          f'⚙️ {car.mileage} \n' \
                          f'🕹 {car.akp} \n' \
                          f'📌 {car.city}'

                if auction_url is not None:
                    caption = caption + f' \n<a href="{auction_url}">Auction</a>'

                media_group = []
                for i in range(len(image_urls)):
                    if i != 0:
                        media_group.append(InputMediaPhoto(media=image_urls[i]))
                    else:
                        media_group.append(
                            InputMediaPhoto(media=image_urls[i], caption=caption, parse_mode=ParseMode.HTML))
                # print(media_group)
                await bot.send_media_group(CHANNEL_ID, media=media_group)
                update_status = update(Car).where(Car.ria_id == car.ria_id).values(is_sended=1)
                session.execute(update_status)
                session.commit()
                is_notif_sended = False
            else:
                if not is_notif_sended:
                    await bot.send_message(CHANNEL_ID, 'Mailing ended. Waiting for the new proposals...')
                    is_notif_sended = not is_notif_sended
        case 'price_changed':
            auction_url: str = await scrap_auction(car.vin_num)
            image_urls = await scrap_images(car.ria_link)
            caption = f'<a href="{car.ria_link}">{car.name}  {car.year}</a> \n' \
                      f'💲<s>{old_car.price_usd}</s> <b>{car.price_usd}</b> \n' \
                      f'🇺🇦 <s>{old_car.price_uah}</s> <b>{car.price_uah}</b> грн \n' \
                      f'⚙️ {car.mileage} \n' \
                      f'🕹 {car.akp} \n' \
                      f'📌 {car.city}'

            if auction_url is not None:
                caption = caption + f' \n<a href="{auction_url}">Auction</a>'

            if car.price_usd > old_car.price_usd:
                caption = f"<b>Seller wanna scam you, price higher!</b> \n" + caption
            else:
                caption = f"<b>Founded better price!</b> \n" + caption

            media_group = []
            for i in range(len(image_urls)):
                if i != 0:
                    media_group.append(InputMediaPhoto(media=image_urls[i]))
                else:
                    media_group.append(
                        InputMediaPhoto(media=image_urls[i], caption=caption, parse_mode=ParseMode.HTML))
            await bot.send_media_group(CHANNEL_ID, media=media_group)

        case 'new_car':
            # variable for prevent on startup spam if database empty (for initial scraping)
            if is_notif_sended:
                auction_url: str = await scrap_auction(car.vin_num)
                image_urls = await scrap_images(car.ria_link)
                caption = f'<a href="{car.ria_link}">{car.name}  {car.year}</a> \n' \
                          f'💲 <b>{car.price_usd}</b> \n' \
                          f'🇺🇦 <b>{car.price_uah}</b> грн \n' \
                          f'⚙️ {car.mileage} \n' \
                          f'🕹 {car.akp} \n' \
                          f'📌 {car.city}'

                caption = "🆕<b>Founded NEW CAR!</b> \n" + caption

                caption = caption + f' \n<a href="{auction_url}">Auction</a>'

                media_group = []
                for i in range(len(image_urls)):
                    if i != 0:
                        media_group.append(InputMediaPhoto(media=image_urls[i]))
                    else:
                        media_group.append(
                            InputMediaPhoto(media=image_urls[i], caption=caption, parse_mode=ParseMode.HTML))
                await bot.send_media_group(CHANNEL_ID, media=media_group)
                is_notif_sended = False