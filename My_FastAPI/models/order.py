from datetime import datetime
from time import timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, DECIMAL, select
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
    total_price = Column(DECIMAL(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.now())
    is_new = Column(Boolean, default=True)
    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, default=None)
    is_delivered = Column(Boolean, default=False)
    is_delivered_time = Column(DateTime, default=None)
    is_canceled = Column(Boolean, default=False)

    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    city = relationship('City', back_populates='orders')

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', foreign_keys=[user_id], back_populates='orders')

    # Поля для менеджера и курьера
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    courier_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    manager = relationship('User', foreign_keys=[manager_id], back_populates='managed_orders')
    courier = relationship('User', foreign_keys=[courier_id], back_populates='courier_orders')


    def update_status(self):
        """Метод для обновления статуса заказа на основе текущих полей."""
        if self.is_canceled:
            self.is_new = False
            self.is_delivered = False

        elif self.is_confirmed and not self.is_canceled:
            self.is_new = False
            self.confirmed_at = datetime.now()  # Время подтверждения

        elif self.is_delivered and not self.is_canceled:
            self.is_new = False
            self.is_confirmed = True
