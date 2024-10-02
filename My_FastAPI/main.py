from fastapi import FastAPI, HTTPException, Request, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db_depends import get_db
from models import Product, Cart
from routers import order, user, sprav, cart
from config import templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, cart_cookie: str = Cookie(None), db: Session = Depends(get_db)):
    query = select(Product).where(Product.is_available == True)
    result = db.execute(query)  # Выполняем запрос
    products = result.scalars().all()  # Получаем все доступные продукты
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    print(cart_instance.items)
    cart_items_count = cart_instance.get_items_count()

    return templates.TemplateResponse('home.html', {"request": request, "products": products, "cart_items_count": cart_items_count})


@app.get("/news", response_class=HTMLResponse)
async def news():
    return templates.TemplateResponse('news.html', {"request": {}, "cart_items_count": 0})


@app.get("/about", response_class=HTMLResponse)
async def about():
    return templates.TemplateResponse('about.html', {"request": {}, "cart_items_count": 0})


app.include_router(order.router)
app.include_router(cart.router)
app.include_router(user.router)
app.include_router(sprav.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, log_level="debug")
