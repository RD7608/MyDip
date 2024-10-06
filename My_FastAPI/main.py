from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from backend.db_depends import get_db
from models import Product, User
from routers import order, user, sprav, cart
from config import templates
from routers.user import get_current_user


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="your_secret_key_1234567890")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):

    query = select(Product).where(Product.is_available == True)  # Получаем все доступные продукты
    result = db.execute(query)  # Выполняем запрос
    products = result.scalars().all()  # Получаем все продукты из запроса

    cart = request.session.get("cart", {})
    cart_items_count = sum(cart.values())
    current_user = get_current_user(request, db)


    context = {
        "request": request,
        "products": products,
        "cart": cart,  # Передаем cart в контекст
        "cart_items_count": cart_items_count,
        "current_user": current_user
    }

    return templates.TemplateResponse('home.html', context)


@app.get("/about", response_class=HTMLResponse)
async def about():
    return templates.TemplateResponse('about.html', {"request": {}, "cart_items_count": 0})


app.include_router(order.router)
app.include_router(cart.router)
app.include_router(user.router)
app.include_router(sprav.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True, log_level="debug")
