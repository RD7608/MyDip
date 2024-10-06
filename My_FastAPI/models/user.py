from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # пароль
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    orders = relationship('Order', back_populates='user')
    profile = relationship('Profile', back_populates='user', uselist=False)  # профиль

    def __repr__(self):
        return f'<User {self.username}>'

    def is_authenticated(self):
        if self.username == "anonymous":
            return False
        return True

    def is_anonymous(self):
        """Проверяет, является ли пользователь анонимным"""
        return self.username == "anonymous"

    def get_id(self):
        """Возвращает уникальный идентификатор пользователя"""
        return self.id



class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, default=None)
    lastname = Column(String, default=None)
    customer_name = Column(String, default=None)
    phone = Column(String, default=None)
    address = Column(String, default=None)

    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    user = relationship('User', back_populates='profile')

    city_id = Column(Integer, ForeignKey('cities.id'), index=True, default=None)
    city = relationship("City", back_populates="profiles")

    is_manager = Column(Boolean, default=False)
    is_courier = Column(Boolean, default=False)
