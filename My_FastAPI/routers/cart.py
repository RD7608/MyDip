from fastapi import APIRouter , Depends , HTTPException , Request , Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi import Cookie
import json

from backend.db_depends import get_db
from models import Cart , Product
from config import templates

router = APIRouter ( prefix="/cart" , tags=["cart"] )


@router.get("/", response_class=HTMLResponse)
async def get_cart(request: Request, cart_cookie: str = Cookie(None), db: Session = Depends(get_db)):
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    cart_items_count = cart_instance.get_items_count()
    product_items = []

    for product_id, quantity in cart_instance.items.items():
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product_items.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": quantity,
                "total_price": product.price * quantity
            })

    context = {
        "request": request,
        "product_items": product_items,
        "cart_items_count": cart_items_count,
        "title": "Корзина"}

    return templates.TemplateResponse("cart.html", context)


@router.post("/add/{product_id}/{quantity}")
async def add_item(product_id: int, quantity: int = 1, response: Response = None, cart_cookie: str = Cookie(None)):
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    cart_instance.add(product_id, quantity)
    response = JSONResponse(content={"message": "Item added successfully", "product_id": product_id, "quantity": quantity})
    response.set_cookie(key="cart_cookie", value=cart_instance.to_json())
    return response


@router.post("/update/{product_id}/{quantity}")
async def update_item(product_id: int, quantity: int, response: Response = None, cart_cookie: str = Cookie(None)):
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    cart_instance.update(product_id, quantity)
    response = JSONResponse(content={"message": "Item updated successfully", "product_id:": product_id, "quantity": quantity})
    response.set_cookie("cart_cookie", cart_instance.to_json()) # Сохраняем обновлённую корзину в куки
    return {"detail": "Item updated successfully", "product_id:": product_id, "quantity": quantity}


@router.post("/remove/{product_id}")
async def remove_item(product_id: int, response: Response = None, cart_cookie: str = Cookie(None)):
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    cart_instance.remove(product_id) # Удаление товара из корзины
    response = JSONResponse(content={"message": "Товар удален", "product_id": product_id}, status_code=200)
    response.set_cookie("cart_cookie", cart_instance.to_json())
    return response


@router.post("/clear")
async def clear_cart(response: Response = None, cart_cookie: str = Cookie(None)):
    cart_instance = Cart.from_json(cart_cookie) if cart_cookie else Cart()
    cart_instance.clear()  # Очищаем корзину
    response = JSONResponse(content={"message": "Корзина очищена"})
    response.set_cookie("cart_cookie", "", expires=0)  # Удаляем куки
    return response
