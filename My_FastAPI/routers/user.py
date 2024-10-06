from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy import exc
from passlib.context import CryptContext

from backend.db_depends import get_db
from models import User, Profile, Order
from schemas import CreateUser, UpdateUser
from config import templates

router = APIRouter(prefix="/user", tags=["user"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_current_user(request: Request, db: Annotated[Session, Depends(get_db)]):
    user_id = request.session.get('user_id')
    if user_id is not None:
        return db.query(User).filter(User.id == user_id).first()
    return db.query(User).filter(User.username == 'anonymous').first()


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("/users/register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        db: Annotated[Session, Depends(get_db)],
                        username: str = Form(...),
                        email: str = Form(...),
                        password: str = Form(...)
                        ):
    # проверяем есть ли такой пользователь
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("/users/register.html",
                                          {"request": request, "error": "Пользователь с таким email уже существует."})

    # хешируем пароль
    hashed_password = pwd_context.hash(password)
    # создаём пользователя
    try:
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # создаём профиль пользователя
        new_profile = Profile(
            user_id=new_user.id,
        )
        db.add(new_profile)
        db.commit()

        return templates.TemplateResponse("/users/login.html",
                                          {"request": request,
                                           "message": f'Регистрация успешна.Ваш логин сайта - {new_user.email}'})

    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка : {str(e)}")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("/users/login.html", {"request": request})


@router.post("/login", response_model=dict)
async def post_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == username).first()

    if user is None or not pwd_context.verify(password, user.password):  # проверяем пароль
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")

    request.session['user_id'] = user.id
    return templates.TemplateResponse("/users/profile.html", {"request": request, "user": user})


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.pop('user_id', None)
    return templates.TemplateResponse("/users/logout.html", {"request": request})


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    if current_user is None:
        return {"message": "Пользователь не аутентифицирован"}
    return {"user": current_user.username}


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, user: UpdateUser):
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user:
        db.execute(update(User).where(User.id == user_id).values(email=user.email,
                                                                 password=user.password))
        db.commit()
        db.execute(update(Profile).where(User.id == user_id).values(firstname=user.firstname,
                                                                    lastname=user.lastname,
                                                                    customer_name=user.customer_name,
                                                                    phone=user.phone,
                                                                    city_id=user.city,
                                                                    address=user.address))

        db.commit()

        return {"status_code": status.HTTP_200_OK,
                "transaction": "Пользователь обновлён!"}
    else:
        raise HTTPException(status_code=404,
                            detail="Пользователь не найден")


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    existing_user = db.scalar(select(User).where(User.id == user_id))
    if existing_user:
        db.execute(delete(Order).where(Order.user_id == user_id))
        db.execute(delete(Profile).where(Profile.user_id == user_id))
        db.execute(delete(User).where(User.id == user_id))
        db.commit()
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Пользователь и связвнные данные удалены!"}
    else:
        raise HTTPException(status_code=404,
                            detail="Пользователь не найден")


@router.delete("/delete-all")
async def delete_all_users(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(delete(Order))
        db.execute(delete(Profile))
        db.execute(delete(User))
        db.commit()
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Все пользователи удалены!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка при удалении пользователей: {str(e)}")

