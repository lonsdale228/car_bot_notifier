from db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vin_num = Column(String, unique=True)
    price = Column(Integer)
    is_sended = Column(Boolean)
    # pictures = relationship("Picture", back_populates="car")


class Picture(Base):
    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vin_num = Column(String, ForeignKey('cars.vin_num'))
    url = Column(String)

    car = relationship("Car", backref=backref("pictures"))
