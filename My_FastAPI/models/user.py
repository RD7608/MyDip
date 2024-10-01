from sqlalchemy import Column , Integer , String , ForeignKey , DateTime , Boolean
from sqlalchemy.orm import relationship
from backend.db import Base


class User ( Base ):
    __tablename__ = 'users'

    id = Column ( Integer , primary_key=True , index=True )
    username = Column ( String )
    email = Column ( String , unique=True , index=True )
    password = Column ( String )  # пароль
    is_active = Column ( Boolean , default=True )
    is_admin = Column ( Boolean , default=False )
    orders = relationship ( 'Order' , back_populates='user' )
    profile = relationship('Profile', back_populates='user', uselist=False) # профиль


class Profile ( Base ):
    __tablename__ = 'profiles'

    id = Column ( Integer , primary_key=True , index=True )
    firstname = Column ( String )
    lastname = Column ( String )
    customer_name = Column ( String )
    phone = Column ( String )
    address = Column ( String )

    user_id = Column ( Integer , ForeignKey ( 'users.id' ) , index=True , nullable=False )
    user = relationship ( 'User' , back_populates='profile' )

    city_id = Column(Integer, ForeignKey('cities.id'), index=True, default=None)
    city = relationship("City", back_populates="profiles")