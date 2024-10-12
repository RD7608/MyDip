from datetime import timezone, datetime

from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from sqlalchemy import func
from typing import Annotated
from sqlalchemy import exc

from backend.db_depends import get_db
from models import User, Order, City, Profile
from other import templates, get_current_user, get_cities, get_products, get_cart_items, delivery_day, get_couriers

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/list")
async def all_orders(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    orders = db.scalars(select(Order).where(Order.user_id == user.id))
    context = {
        'title': 'Заказы',
        'orders': orders,
        'cart_items_count': request.session.get("cart_items_count", 0),
        'user': user
    }
    return templates.TemplateResponse(request, "/order/orders.html", context)


@router.get("/manager")
async def manager_orders(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user.profile.is_manager and not user.is_admin:
        message = f"Вы не менеджер!"
        # Инициализируем список сообщений в сессии, если он еще не существует
        if 'messages' not in request.session:
            request.session['messages'] = []
        request.session['messages'].append(message)  # Добавляем сообщение в список

        return RedirectResponse(url=f"/user/profile/{user.id}", status_code=302)

    # Устанавливаем фильтры
    if request.query_params.get('reset'):
        request.session['date_filter'] = ""
        request.session['city_filter'] = "all"
        request.session['manager_filter'] = "no_manager"
    else:  # Если фильтры не были изменены, то сохраняем их в сессию
        request.session['date_filter'] = request.query_params.get('date', str(datetime.now().date()))
        request.session['city_filter'] = request.query_params.get('city', 'all')
        request.session['manager_filter'] = request.query_params.get('manager', 'no_manager')


    # Получение текущих значений фильтров из сессии
    date_filter = request.session.get('date_filter', str(datetime.now().date()))
    city_filter = request.session.get('city_filter', 'all')
    manager_filter = request.session.get('manager_filter', 'no_manager')

    cities = get_cities(db)  # Получаем список городов для формы

    couriers = get_couriers(db)  # Получаем список курьеров для формы


    # Фильтрация по подтвержденным заказам
    orders = db.query(Order).filter(Order.is_confirmed == True)

    # Фильтрация по дате
    if date_filter:
        orders = orders.filter(func.date(Order.delivery_date) == date_filter)

    # Фильтрация по городу
    if city_filter and city_filter != 'all':
        orders = orders.filter(Order.city_id == city_filter)

        # Фильтрация по заказам для менеджера
    if manager_filter == 'my_orders':
        orders = orders.filter(Order.manager == user)
    if manager_filter == 'no_manager':
        orders = orders.filter(Order.manager == None)

    orders = orders.all()  # Получение отфильтрованных заказов для отображения в форме

    context = {
        'title': 'Заказы',
        'messages': request.session.get("messages", []),
        'orders': orders,
        'cities': cities,
        'couriers': couriers,
        'cart_items_count': request.session.get("cart_items_count", 0),
        'user': user,
        'date_filter': date_filter,
        'city_filter': city_filter,
        'manager_filter': manager_filter,
    }
    return templates.TemplateResponse(request, "/order/orders_manager.html", context)


@router.post("/assign_courier/{order_id}")
async def assign_courier(request: Request, order_id: int, courier_id: int = Form(...), db: Session = Depends(get_db)):
    """ Устанавливает курьера для заказа

    order_id - id заказа
    courier_id - id курьера

    """
    user = get_current_user(request, db)
    try:
        # Получаем заказ по order_id
        order = db.scalar(select(Order).where(Order.id == order_id))

        # Получаем курьера по courier_id полученному из формы
        courier = db.scalar(select(User).where(User.id == courier_id))

        # Назначение курьера и менеджера
        order.courier = courier  # Устанавливаем курьера
        order.manager = user  # Устанавливаем менеджера (текущий пользователь)
        db.commit()  # Сохраняем изменения

        message = f'Курьер {courier.username} назначен для выполнения заказа {order.number}.'
    except Order.DoesNotExist:
        message = 'Заказ не найден.'
    except User.DoesNotExist:
        message = 'Курьер не найден.'
    except Exception as e:
        message = f'Ошибка: {str(e)}'
    # Инициализируем список сообщений в сессии, если он еще не существует
    if 'messages' not in request.session:
        request.session['messages'] = []
    request.session['messages'].append(message)  # Добавляем сообщение в список

    # Получаем текущие фильтры из сессии
    date_filter = request.session.get('date_filter', str(datetime.now().date()))
    city_filter = request.session.get('city_filter', 'all')
    manager_filter = request.session.get('manager_filter', 'no_manager')
    # Перенаправляем обратно на страницу менеджера с фильтрами
    url = f"/order/manager?date={date_filter}&city={city_filter}&manager={manager_filter}"
    return RedirectResponse(url=url, status_code=302)


@router.post("/cancel/{order_id}")
async def order_cancel(request: Request, db: Annotated[Session, Depends(get_db)], order_id: int):
    user = get_current_user(request, db)
    order = db.scalar(select(Order).where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order.is_canceled = True
    order.manager = user  # Назначение текущего пользователя менеджером
    order.update_status()  # Обновление статуса заказа
    db.commit()  # Сохранение изменений в базе данных
    message = f'Заказ {order.number} отменен.'

    # Получаем текущие фильтры из сессии
    date_filter = request.session.get('date_filter', str(datetime.now().date()))
    city_filter = request.session.get('city_filter', 'all')
    manager_filter = request.session.get('manager_filter', 'no_manager')

    if 'messages' not in request.session:
        request.session['messages'] = []
    request.session['messages'].append(message)  # Добавляем сообщение в список

    # Перенаправляем обратно на страницу менеджера с фильтрами
    url = f"/order/manager?date={date_filter}&city={city_filter}&manager={manager_filter}"
    return RedirectResponse(url=url, status_code=302)


@router.get("/courier")
async def courier_orders(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user.profile.is_courier and not user.is_admin:
        message = f"Вы не курьер!"
        # Инициализируем список сообщений в сессии, если он еще не существует
        if 'messages' not in request.session:
            request.session['messages'] = []
        request.session['messages'].append(message)  # Добавляем сообщение в список

        return RedirectResponse(url=f"/user/profile/{user.id}", status_code=302)

    # Устанавливаем фильтры
    if request.query_params.get('reset'):
        request.session['date_filter'] = ""
        request.session['courier_filter'] = "no_delivery"
    else:
        request.session['date_filter'] = request.query_params.get('date', str(datetime.now().date()))
        request.session['courier_filter'] = request.query_params.get('courier', 'no_delivery')

    # Получаем текущие фильтры из сессии
    date_filter = request.session.get('date_filter', str(datetime.now().date()))
    courier_filter = request.session.get('courier_filter', 'no_delivery')

    # Фильтрация по курьеру
    orders = db.query(Order).filter(Order.courier == user)

    # Фильтрация по дате
    if date_filter:
        orders = orders.filter(func.date(Order.delivery_date) == date_filter)

    # Фильтрация по статусу доставки
    if courier_filter == 'no_delivery':
        orders = orders.filter(Order.is_delivered == False)
    elif courier_filter == 'my_orders':
        orders = orders.filter(Order.courier == user)

    # Получение отфильтрованных заказов
    orders = orders.all()

    context = {
        'title': 'Заказы',
        'messages': request.session.get("messages", []),
        'orders': orders,
        'cart_items_count': request.session.get("cart_items_count", 0),
        'user': user,
        'date_filter': date_filter,
        'courier_filter': courier_filter,
        'current_time': datetime.now().strftime('%H:%M')
    }
    return templates.TemplateResponse(request, "/order/orders_courier.html", context)


@router.post("/confirm_delivery/{order_id}")
def confirm_delivery(request: Request, order_id: int, delivered_time: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    # Попытка получить заказ по ID
    order = db.scalar(select(Order).where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Преобразование строки времени в объект datetime
        delivered_time_dt = datetime.strptime(delivered_time, "%H:%M").replace(year=datetime.now().year,
                                                                               month=datetime.now().month,
                                                                               day=datetime.now().day)

        # Обновление информации о доставке
        order.is_delivered = True  # устанавливаем статус доставки в True
        order.is_delivered_time = delivered_time_dt  # Дата и время доставки
        order.update_status()  # Обновление статуса заказа
        db.commit()  # Сохранение изменений в базе данных
        message = f'Время доставки заказа {order.number} - {order.is_delivered_time}.'

    except Exception as e:
        db.rollback()  # Откат изменений в случае ошибки
        raise HTTPException(status_code=500, detail=f"Error during delivery confirmation: {str(e)}")

    if 'messages' not in request.session:
        request.session['messages'] = []
    request.session['messages'].append(message)  # Добавляем сообщение в список

    # Получаем текущие фильтры из сессии
    date_filter = request.session.get('date_filter')
    courier_filter = request.session.get('courier_filter')

    # Формирование URL для перенаправления
    url = f"/order/courier?date={date_filter}&courier={courier_filter}"

    return RedirectResponse(url=url, status_code=302)


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
    cart_items, total_price = get_cart_items(cart, db)

    user = get_current_user(request, db)

    context = {
        'title': 'Оформление заказа',
        'cities': get_cities(db),
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': request.session.get('cart_items_count', 0),
        'user': user,
        'delivery_day': delivery_day()
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
