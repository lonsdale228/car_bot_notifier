from db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref


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

    bidfax_url = Column(String)
    # pictures = relationship("Picture", back_populates="car")


class Picture(Base):
    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vin_num = Column(String, ForeignKey('cars.vin_num'))
    url = Column(String)

    car = relationship("Car", backref=backref("pictures"))
