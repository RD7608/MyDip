from datetime import timezone, datetime

from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy import exc

from backend.db_depends import get_db
from models import User, Order, City
from schemas import CreateOrder, UpdateOrder
from other import templates, get_current_user, get_cities, get_products

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/list")
async def all_orders(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    print(user.id, user.username)
    orders = db.scalars(select(Order).where(Order.user_id == user.id))
    context = {
        'title': 'Заказы',
        'orders': orders,
        'cart_items_count': request.session.get("cart_items_count", 0),
        'user': user
    }
    return templates.TemplateResponse(request, "/order/orders.html", context)


@router.get("/order_id")
async def order_by_id(db: Annotated[Session, Depends(get_db)], order_id: int):
    order = db.scalar(select(Order).where(Order.id == order_id))
    if order:
        return order
    else:
        raise HTTPException(status_code=404,
                            detail="Order was not found")


@router.get("/create")
async def order_form(request: Request, db: Annotated[Session, Depends(get_db)]):
    cart = request.session.get('cart', {})
    cities = get_cities(db)
    products = get_products(db)
    cart_items = []  # Список для хранения деталей продуктов в корзине
    total_price = 0  # Общая сумма
    for product in products:
        product_quantity = cart[str(product.id)]  # Получаем количество товаров
        product_total_price = product.price * product_quantity  # Считаем сумму для этого продукта

        # Добавляем в список детали продукта
        cart_items.append({
            'product': product,
            'quantity': product_quantity,
            'total_price': product_total_price
        })

        # Добавляем к общей сумме
        total_price += product_total_price

    user = get_current_user(request, db)

    context = {
        'cities': cities,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': request.session.get('cart_items_count', 0),
        'title': 'Оформление заказа',
        'user': user
    }

    return templates.TemplateResponse(request, 'order/order_form.html', context)


@router.post("/create")
async def order_create(request: Request,
                       db: Annotated[Session, Depends(get_db)],
                       customer_name: str = Form(...),
                       customer_email: str = Form(...),
                       customer_phone: str = Form(...),
                       city: int = Form(...),
                       address: str = Form(...),
                       delivery_date: datetime = Form(...),
                       total_price: float = Form(...),
                       ):
    number = get_next_order_number(city, db)
    cart = request.session.get('cart', {})
    user = get_current_user(request, db)

    try:
        new_order = Order(
            user_id=user.id,
            number=number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            city_id=city,
            address=address,
            delivery_date=delivery_date,
            items=str(cart),
            total_price=total_price,
            is_confirmed=True
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        new_order.is_confirmed = True
        new_order.update_status()
        db.commit()

        # Сохраняем в сессию
        request.session['cart'] = {}
        request.session['cart_items_count'] = 0
        context = {
            'order': new_order,
            'title': 'Заказ оформлен',
            'user': user
        }

        return templates.TemplateResponse(request, 'order/order_success.html', context)

    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cancel")
async def order_cancel(db: Annotated[Session, Depends(get_db)], order_id: int):
    existing_order = db.scalar(select(Order).where(Order.id == order_id))
    if existing_order:
        existing_order.is_canceled=True
        existing_order.update_status()
        db.commit()
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Order is cancelled!"}

    else:
        raise HTTPException(status_code=404,
                            detail="Order was not found to cancel")


def get_next_order_number(city_id, db):
    current_date = datetime.now().strftime('%d%m%Y')
    city = db.scalar(select(City).where(City.id == city_id))
    city_abbreviation = city.abbreviation
    last_order = db.scalars(
        select(Order).where(Order.city_id == city_id).order_by(Order.created_at.desc())).first()
    if last_order:
        last_sequence = int(last_order.number.split('-')[-1])
        order_sequence = str(last_sequence + 1).zfill(3)
    else:
        order_sequence = '001'
    return f"{city_abbreviation}-{current_date}-{order_sequence}"
