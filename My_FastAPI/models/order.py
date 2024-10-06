from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.db import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String)
    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    address = Column(String)
    delivery_date = Column(DateTime)
    items = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    is_new = Column(Boolean, default=True)
    is_confirmed = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    is_delivered_time = Column(DateTime, default=None)
    is_canceled = Column(Boolean, default=False)

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    city = relationship('City', back_populates='orders')

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='orders')
