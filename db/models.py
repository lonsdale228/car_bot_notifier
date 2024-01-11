from db.database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ria_id = Column(String, unique=True)
    ria_link = Column(String)
    name = Column(String)
    year = Column(Integer)
    city = Column(String)
    mileage = Column(String)
    akp = Column(String)
    vin_num = Column(String)
    price_usd = Column(Integer)
    prev_price = Column(Integer)
    price_uah = Column(Integer)
    is_sended = Column(Boolean)

    auction_url = Column(String)