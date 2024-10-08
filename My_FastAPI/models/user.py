from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.db import Base
from .order import Order


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, default=None)
    lastname = Column(String, default=None)
    customer_name = Column(String, default=None)
    phone = Column(String, default=None)
    address = Column(String, default=None)

    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    user = relationship('User', foreign_keys=[user_id], back_populates='profile')

    city_id = Column(Integer, ForeignKey('cities.id'), index=True, default=None)
    city = relationship("City", back_populates="profiles")

    is_manager = Column(Boolean, default=False)
    is_courier = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # пароль
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    profile = relationship('Profile', foreign_keys=[Profile.user_id], back_populates='user', uselist=False)  # профиль

    orders = relationship('Order', foreign_keys=[Order.user_id], back_populates='user')
    managed_orders = relationship('Order', foreign_keys=[Order.manager_id], back_populates='manager')
    courier_orders = relationship('Order', foreign_keys=[Order.courier_id], back_populates='courier')

    def is_authenticated(self):
        # Проверяет, является ли пользователь аутентифицированным
        if self.username == "anonymous":  # если пользователь анонимный
            return False
        return True

    def is_anonymous(self):
        """Проверяет, является ли пользователь анонимным"""
        return self.username == "anonymous"
