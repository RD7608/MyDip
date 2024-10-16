from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import City, Product, User, Profile
from fastapi.templating import Jinja2Templates
from datetime import date, timedelta

templates = Jinja2Templates(directory='templates')


def get_current_user(request: Request, db: Session) -> User:
    """Получение текущего пользователя.

    :param request: Запрос
    :param db: Сессия SQLAlchemy
    :return: User
    """
    # Получение id пользователя из сессии
    user_id = request.session.get('user_id')
    if user_id is not None:  # Если в сессии есть user_id, то возвращаем пользователя
        return db.scalar(select(User).where(User.id == user_id))

    # Если в сессии нет user_id, то возвращаем анонимного пользователя
    # (созданного заранее в базе)
    return db.scalar(select(User).where(User.username == 'anonymous'))


def get_cart_items(cart, db: Session):
    """ Получает список товаров из корзины
        Создает список товаров содержащихся в корзине и добавляет в него цену и сумму товаров
    param
     cart: корзина пользователя в виде словаря {id: quantity}

    Возвращает список товаров в корзине и общую сумму товаров

    """
    cart_items = []  # Пустой список для хранения деталей продуктов в корзине
    total_price = 0  # Общая сумма

    products = get_products(db, cart)  # Получение данных из базы по товарам находящимся в корзине
    for product in products:
        product_quantity = cart[str(product.id)]  # Получаем количество товара в корзине
        product_total_price = product.price * product_quantity  # Считаем сумму для этого продукта

        # Добавляем в список детали продукта
        cart_items.append({
            'product': product,  # Добавляем товар
            'quantity': product_quantity,  # Количество товара
            'total_price': product_total_price  # Сумма товара
        })

        # Добавляем сумму товара к общей сумме товаров
        total_price += product_total_price

    return cart_items, total_price


def get_cities(db: Session):
    """
    Получение всех городов из базы данных.

    :param db: Сессия SQLAlchemy
    :return: Список городов
    """
    return db.query(City).all()


def get_couriers(db: Session):
    """
    Получение всех курьеров из базы данных.

    :param db: Сессия SQLAlchemy
    :return: Список курьеров
    """

    return db.scalars(select(User).join(User.profile).where(Profile.is_courier)).all()


def get_products(db: Session, cart=None):
    """
    Получение продуктов из базы данных.

    :param
        db: Сессия SQLAlchemy
        cart: Список продуктов в корзине

    :return: Список продуктов
    """
    if cart is not None:
        product_ids = list(map(int, cart.keys()))  # Преобразуем ключи в целые числа для отбора товаров в запросе
        # Формируем запрос для получения товаров по их идентификаторам
        stmt = select(Product).where(Product.id.in_(product_ids))
    else:
        # Формируем запрос для получения активных и доступных товаров
        stmt = select(Product).where(Product.is_active, Product.is_available)

    # Выполняем запрос
    products = db.execute(stmt).scalars().all()

    return products


# Функция для получения текущей даты плюс один день
def delivery_day():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return tomorrow
