from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from typing import Annotated
from sqlalchemy import exc


from backend.db_depends import get_db
from models import User, Profile, Order
from schemas import CreateUser, UpdateUser
from other import get_current_user, templates, get_cities

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, db: Annotated[Session, Depends(get_db)]):
    user = get_current_user(request, db)
    return templates.TemplateResponse("/users/register.html",
                                      {"request": request,
                                       "cart_items_count": request.session.get("cart_items_count", 0),
                                       "user": user})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request,
                        db: Annotated[Session, Depends(get_db)],
                        username: str = Form(...),
                        email: str = Form(...),
                        password: str = Form(...)
                        ):
    # ищем пользователя в базе по email (в базе это поле уникально)
    existing_user = db.query(User).filter(User.email == email).first()
    message = ""
    if email == "" or password == "" or username == "anonymous":
        message = "Нельзя создать пользователя! (anonymous, с пустой почтой или паролем)"
    elif existing_user:
        message = "Пользователь с таким email уже существует."

    if message != "":
        return templates.TemplateResponse("/users/register.html",
                                          {"request": request,
                                           "error": message,
                                           "cart_items_count": request.session.get("cart_items_count", 0),
                                           "user": get_current_user(request, db)})

    # создаём пользователя
    try:
        new_user = User(
            username=username,
            email=email,
            password=password,
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
        user = get_current_user(request, db)
        return templates.TemplateResponse("/users/login.html",
                                          {"request": request,
                                           "message": f'Регистрация успешна.Ваш логин сайта - {new_user.email}',
                                           "cart_items_count": request.session.get("cart_items_count", 0),
                                           'user': user})

    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка : {str(e)}")


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, db: Annotated[Session, Depends(get_db)]):
    user = get_current_user(request, db)
    return templates.TemplateResponse("/users/login.html",
                                      {"request": request,
                                       "cart_items_count": request.session.get("cart_items_count", 0),
                                       'user': user})


@router.post("/login", response_model=dict)
async def post_login(request: Request, username: str = Form(...), password: str = Form(...),
                     db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == username).first()

    if user is None or not user.check_password(password):  # проверяем пароль
        raise HTTPException(status_code=400, detail="Неправильный логин или пароль")

    request.session['user_id'] = user.id
    return RedirectResponse(url=f"/user/profile/{user.id}", status_code=302)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, db: Annotated[Session, Depends(get_db)]):
    request.session.pop('user_id', None)
    user = get_current_user(request, db)
    return templates.TemplateResponse("/users/logout.html",
                                      {"request": request,
                                       "cart_items_count": request.session.get("cart_items_count", 0),
                                       "user": user})


@router.get("/profile/{user_id}", response_class=HTMLResponse)
async def get_profile(request: Request, db: Annotated[Session, Depends(get_db)], user_id: int = None):
    messages = request.session.get('messages', [])

    user = get_current_user(request, db)  # получаем текущего пользователя
    if not user.is_authenticated():
        raise HTTPException(status_code=401, detail="Unauthorized")
    print(user_id)
    if not user_id:  # если пользователь не передан
        user_id = user.id

    user_form = db.query(User).filter(User.id == user_id).first()

    cities = get_cities(db)  # получаем список городов

    return templates.TemplateResponse("/users/profile.html",
                                      {"request": request,
                                       "cities": cities,
                                       "cart_items_count": request.session.get("cart_items_count", 0),
                                       "user": user,
                                       "user_form": user_form,
                                       "messages": messages})


@router.post("/update")
async def update_form(request: Request,
                      db: Annotated[Session, Depends(get_db)],
                      username: str = Form(...),
                      firstname: str = Form(...),
                      lastname: str = Form(...),
                      customer_name: str = Form(...),
                      city: int = Form(...),
                      address: str = Form(...),
                      phone: str = Form(...),
                      is_manager: bool = Form(default=False),
                      is_courier: bool = Form(default=False),
                      user_id: int = Form(...)):

    try:
        user = get_current_user(request, db)  # получаем текущего пользователя
        if not user.is_authenticated():
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not user_id:
            raise HTTPException(status_code=401, detail="user_id is required")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')

        if user:
            if user.is_admin:
                is_manager = True
                is_courier = True


            # Обновление пользователя
            db.execute(
                update(User)
                .where(User.id == user_id)
                .values(username=username)
            )

            # Обновление профиля - связываем профиль с пользователем через user_id
            db.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(
                    firstname=firstname,
                    lastname=lastname,
                    customer_name=customer_name,
                    city_id=city,
                    address=address,
                    phone=phone,
                    is_manager=is_manager,
                    is_courier=is_courier
                )
            )
            db.commit()

            message = f"Профиль {user.email} был обновлен"
            # Инициализируем список сообщений в сессии, если он еще не существует
            if 'messages' not in request.session:
                request.session['messages'] = []
            request.session['messages'].append(message)  # Добавляем сообщение в список

            return RedirectResponse(url=f"/user/profile/{user.id}", status_code=302)

        else:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_user(request: Request, db: Annotated[Session, Depends(get_db)]):
    user = get_current_user(request, db)
    if user.is_admin:
        users = db.query(User).all()

        context = {
            "request": request,
            "users": users,
            "user": user,
            "title": "Пользователи",
        }
        return templates.TemplateResponse("/users/users.html", context)

    message = f"Вы не администратор"
    # Инициализируем список сообщений в сессии, если он еще не существует
    if 'messages' not in request.session:
        request.session['messages'] = []
    request.session['messages'].append(message)  # Добавляем сообщение в список

    return RedirectResponse(url=f"/user/profile/{user.id}", status_code=302)


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
