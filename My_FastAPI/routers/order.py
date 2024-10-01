from datetime import timezone , datetime

from fastapi import APIRouter , Depends , status , HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import insert , select , update , delete
from typing import Annotated
from sqlalchemy import exc

from backend.db_depends import get_db
from models import User , Order , City
from schemas import CreateOrder , UpdateOrder

router = APIRouter ( prefix="/order" , tags=["order"] )


@router.get ( "/" )
async def all_orders(db: Session = Depends ( get_db )):
    orders = db.scalars ( select ( Order ) ).all ()
    return orders


@router.get ( "/order_id" )
async def order_by_id(db: Annotated[Session , Depends ( get_db )] , order_id: int):
    order = db.scalar ( select ( Order ).where ( Order.id == order_id ) )
    if order:
        return order
    else:
        raise HTTPException ( status_code=404 ,
                              detail="Order was not found" )


@router.post ( "/create" )
async def create_order(db: Annotated[Session , Depends ( get_db )] , order: CreateOrder):
    order_number = get_next_order_number ( order.city , db )
    new_order = Order (
        number=order_number ,
        customer_name=order.customer_name ,
        customer_email=order.customer_email ,
        customer_phone=order.customer_phone ,
        city=order.city ,
        address=order.address ,
        delivery_date=order.delivery_date ,
        items=order.items
    )

    try:
        db.add ( new_order )
        db.commit ()
        db.refresh ( new_order )
        return new_order
    except exc.SQLAlchemyError as e:
        raise HTTPException ( status_code=500 , detail=str ( e ) )


@router.put ( "/update" )
async def update_order(db: Annotated[Session , Depends ( get_db )] , order_id: int , order: UpdateOrder):
    existing_order = db.scalar ( select ( Order ).where ( Order.id == order_id ) )
    if existing_order:
        db.execute ( update ( Order ).where ( Order.id == order_id ).values ( customer_name=order.customer_name ,
                                                                              delivery_date=order.delivery_date ,
                                                                              products=order.products ) )
        db.commit ()
        return {"status_code": status.HTTP_200_OK ,
                "transaction": "Order update is successful!"}

    else:
        raise HTTPException ( status_code=404 ,
                              detail="Order was not found to update" )


@router.put ( "/cancel" )
async def cancel_order(db: Annotated[Session , Depends ( get_db )] , order_id: int):
    existing_order = db.scalar ( select ( Order ).where ( Order.id == order_id ) )
    if existing_order:
        db.execute ( update ( Order ).where ( Order.id == order_id ).values ( is_new=False ,
                                                                              is_canceled=True ) )
        db.commit ()
        return {"status_code": status.HTTP_200_OK ,
                "transaction": "Order is cancelled!"}

    else:
        raise HTTPException ( status_code=404 ,
                              detail="Order was not found to cancel" )


async def get_next_order_number(city_id , db):
    current_date = datetime.now ().strftime ( '%d%m%Y' )
    city = db.scalar ( select ( City ).where ( City.id == city_id ) )
    city_abbreviation = city.abbreviation
    last_order = db.scalars (
        select ( Order ).where ( Order.city_id == city_id ).order_by ( Order.created_at.desc () ) ).first ()
    if last_order:
        last_sequence = int ( last_order.order_number.split ( '-' )[-1] )
        order_sequence = str ( last_sequence + 1 ).zfill ( 3 )
    else:
        order_sequence = '001'
    return f"{city_abbreviation}-{current_date}-{order_sequence}"
