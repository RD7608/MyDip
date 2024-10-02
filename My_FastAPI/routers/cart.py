from fastapi import APIRouter , Depends , HTTPException , Request , Response
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi import Cookie
import json

from backend.db_depends import get_db
from models import Cart , Product
from config import templates

router = APIRouter ( prefix="/cart" , tags=["cart"] )


@router.get("/")
async def get_cart(cart: str = Cookie(None)):
    cart_instance = Cart.from_json(cart) if cart else Cart()
    return cart_instance.items


@router.post("/add/{product_id}")
async def add_item(product_id: int, quantity: int = 1, response: Response = None, cart: str = Cookie(None)):
    cart_instance = Cart.from_json(cart) if cart else Cart()
    cart_instance.add(product_id, quantity)

    response = JSONResponse(content={"message": "Item added successfully", "cart": cart_instance.items})
    response.set_cookie(key="cart", value=cart_instance.to_json(), httponly=True)
    return response


@router.put("/update/{product_id}/{quantity}")
async def update_item(product_id: int, quantity: int, response: Response = None, cart: str = Cookie(None)):
    cart_instance = Cart.from_json(cart) if cart else Cart()
    cart_instance.update(product_id, quantity)

    response = JSONResponse(content={"message": "Item updated successfully", "cart": cart_instance.items})
    response.set_cookie(key="cart", value=cart_instance.to_json(), httponly=True)
    return response


@router.delete("/remove/{product_id}")
async def remove_item(product_id: int, response: Response = None, cart: str = Cookie(None)):
    cart_instance = Cart.from_json(cart) if cart else Cart()
    cart_instance.remove(product_id)

    response = JSONResponse(content={"message": "Item removed successfully", "cart": cart_instance.items})
    response.set_cookie(key="cart", value=cart_instance.to_json(), httponly=True)
    return response


@router.delete("/clear")
async def clear_cart(response: Response = None, cart: str = Cookie(None)):
    cart_instance = Cart.from_json(cart) if cart else Cart()
    cart_instance.clear()  # Очищаем корзину

    response = JSONResponse(content={"message": "Cart cleared", "cart": cart_instance.items})
    response.set_cookie(key="cart", value=cart_instance.to_json(), httponly=True)
    return response
