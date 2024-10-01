from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.db import Base



class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    abbreviation = Column(String, index=True)
    orders = relationship ( 'Order' , back_populates='city' )
    profiles = relationship ( 'Profile' , back_populates='city' )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column ( String )
    price = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=False)