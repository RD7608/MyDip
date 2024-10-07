from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from backend.db_depends import get_db
from routers import order, user, sprav, cart
from other import templates, get_current_user, get_products


app = FastAPI()  # Создание экземпляра FastAPI

app.add_middleware(SessionMiddleware, secret_key="your_secret_key_1234567890")  # Секретный ключ для сессии

app.mount("/static", StaticFiles(directory="static"), name="static") # Маршрутизация для статики


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Главная страница
        Выводит доступные для заказа товары на страницу
        можно добавлять/убавлять товары в корзине,
        перейти в корзину или оформить заказ
    """
    # Получаем все доступные для заказа товары из базы данных
    products = get_products(db)

    cart = request.session.get("cart", {})
    cart_items_count = sum(cart.values())
    current_user = get_current_user(request, db)

    context = {
        "request": request,
        "products": products,
        "cart": cart,  # Передаем cart в контекст
        "cart_items_count": cart_items_count,
        "user": current_user
    }

    return templates.TemplateResponse('home.html', context)


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, db: Session = Depends(get_db)):
    """
     Выводит информацию о предприятии
    """

    user = get_current_user(request, db)
    cart_items_count = request.session.get("cart_items_count", 0)

    return templates.TemplateResponse('about.html', {"request": {},
                                                     "cart_items_count": cart_items_count,
                                                     "user": user})


app.include_router(order.router)
app.include_router(cart.router)
app.include_router(user.router)
app.include_router(sprav.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True, log_level="debug")
