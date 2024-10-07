from fastapi import Request
from sqlalchemy.orm import Session
from models import City, Product, User
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')


def get_current_user(request: Request, db: Session) -> User:
    """Получение текущего пользователя.

    :param request: Запрос
    :param db: Сессия SQLAlchemy
    :return: User
    """
    # Получение id пользователя из сессии
    user_id = request.session.get('user_id')
    if user_id is not None:
        return db.query(User).filter(User.id == user_id).first()

    # Если в сессии нет user_id, то возвращаем анонимного пользователя
    # (созданного заранее в базе)
    return db.query(User).filter(User.username == 'anonymous').first()


def get_cities(db: Session):
    """
    Получение всех городов из базы данных.

    :param db: Сессия SQLAlchemy
    :return: Список городов
    """
    return db.query(City).all()


def get_products(db: Session):
    """
    Получение всех продуктов из базы данных.

    :param db: Сессия SQLAlchemy
    :return: Список продуктов
    """
    return db.query(Product).filter(Product.is_active == True).all()
