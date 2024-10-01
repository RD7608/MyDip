from fastapi import APIRouter , Depends , status , HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert , select , update , delete
from typing import Annotated
from sqlalchemy import exc

from backend.db_depends import get_db
from models import User , Profile , Order
from schemas import CreateUser , UpdateUser

router = APIRouter ( prefix="/user" , tags=["user"] )


@router.get ( "/" )
async def all_users(db: Annotated[Session , Depends ( get_db )]):
    try:
        users = db.scalars ( select ( User ) ).all ()
        return users

    except exc.SQLAlchemyError as e:
        db.rollback ()
        raise HTTPException ( status_code=500 ,
                              detail=f"Ошибка : {str ( e )}" )
    except Exception as e:
        db.rollback ()
        raise HTTPException ( status_code=500 ,
                              detail=f"Ошибка : {str ( e )}" )


@router.get ( "/user_id" )
async def user_by_id(db: Annotated[Session , Depends ( get_db )] , user_id: int):
    user = db.scalar ( select ( User ).where ( User.id == user_id ) )
    if user:
        return user
    else:
        raise HTTPException ( status_code=404 ,
                              detail="Пользователь не найден" )


@router.get ( "/user_id/orders" )
async def orders_by_user_id(db: Annotated[Session , Depends ( get_db )] , user_id: int):
    user = db.scalar ( select ( User ).where ( User.id == user_id ) )
    if user:
        orders = db.scalars ( select ( Order ).where ( Order.user_id == user_id ) ).all ()
        if orders:
            return orders
        else:
            raise HTTPException ( status_code=404 ,
                                  detail="У пользователя нет заказов" )
    else:
        raise HTTPException ( status_code=404 ,
                              detail="Пользователь не найден" )


@router.post ( "/create" )
async def create_user(db: Annotated[Session , Depends ( get_db )] , user: CreateUser):
    try:
        new_user = User ( username=user.username , email=user.email , password=user.password ,
                          is_active=user.is_active , is_admin=user.is_admin , )
        db.add ( new_user )
        db.commit ()
        db.refresh ( new_user )

        new_profile = Profile ( user_id=new_user.id ,
                                firstname=user.firstname ,
                                lastname=user.lastname ,
                                customer_name=user.customer_name ,
                                phone=user.phone ,
                                city_id=user.city ,
                                address=user.address )
        db.add ( new_profile )
        db.commit ()
        return {"status_code": status.HTTP_201_CREATED ,
                "transaction": "Successful"}
    except exc.IntegrityError as e:
        db.rollback ()
        raise HTTPException ( status_code=409 ,
                              detail=f"Пользователь c таким email {user.email} уже существует" )
    except exc.SQLAlchemyError as e:
        db.rollback ()
        raise HTTPException ( status_code=500 ,
                              detail=f"Ошибка : {str ( e )}" )


@router.put ( "/update" )
async def update_user(db: Annotated[Session , Depends ( get_db )] , user_id: int , user: UpdateUser):
    existing_user = db.scalar ( select ( User ).where ( User.id == user_id ) )
    if existing_user:
        db.execute ( update ( User ).where ( User.id == user_id ).values ( email=user.email ,
                                                                           password=user.password ) )
        db.commit ()
        db.execute ( update ( Profile ).where ( User.id == user_id ).values ( firstname=user.firstname ,
                                                                              lastname=user.lastname ,
                                                                              customer_name=user.customer_name ,
                                                                              phone=user.phone ,
                                                                              city_id=user.city ,
                                                                              address=user.address ) )

        db.commit ()

        return {"status_code": status.HTTP_200_OK ,
                "transaction": "Пользователь обновлён!"}
    else:
        raise HTTPException ( status_code=404 ,
                              detail="Пользователь не найден" )


@router.delete ( "/delete" )
async def delete_user(db: Annotated[Session , Depends ( get_db )] , user_id: int):
    existing_user = db.scalar ( select ( User ).where ( User.id == user_id ) )
    if existing_user:
        db.execute ( delete ( Order ).where ( Order.user_id == user_id ) )
        db.execute ( delete ( Profile ).where ( Profile.user_id == user_id ) )
        db.execute ( delete ( User ).where ( User.id == user_id ) )
        db.commit ()
        return {"status_code": status.HTTP_200_OK ,
                "transaction": "Пользователь и связвнные данные удалены!"}
    else:
        raise HTTPException ( status_code=404 ,
                              detail="Пользователь не найден" )


@router.delete ( "/delete-all" )
async def delete_all_users(db: Annotated[Session , Depends ( get_db )]):
    try:
        db.execute ( delete ( Order ) )
        db.execute ( delete ( Profile ) )
        db.execute ( delete ( User ) )
        db.commit ()
        return {"status_code": status.HTTP_200_OK ,
                "transaction": "Все пользователи удалены!"}

    except Exception as e:
        db.rollback ()
        raise HTTPException ( status_code=500 ,
                              detail=f"Ошибка при удалении пользователей: {str ( e )}" )
