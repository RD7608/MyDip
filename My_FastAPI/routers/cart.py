from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi import Cookie

from backend.db_depends import get_db
from models import Cart, Product
from other import templates, get_current_user, get_products, get_cart_items

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_class=HTMLResponse)
async def get_cart(request: Request, db: Session = Depends(get_db)):
    """
    Получает корзину из сессии и выводит ее на страницу
    :param request:
    :param db:
    :return:
    """
    cart = request.session.get('cart', {})
    cart_items, total_price = get_cart_items(cart, db)
    cart_items_count = request.session.get('cart_items_count', 0)
    user = get_current_user(request, db)
    context = {
        "request": request,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': cart_items_count,
        "title": "Корзина",
        'user': user
    }

    return templates.TemplateResponse("cart.html", context)


@router.post("/add/{product_id}")
async def add_item(request: Request, product_id: int, next: str = Form(...)):
    """ Добавление товара в корзину
    параметры:
    product_id - идентификатор товара
    next - страница, на которую будет перенаправлен пользователь
    """

    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id not in cart:
        cart[product_id] = 1
    else:
        cart[product_id] += 1

    request.session['cart'] = cart
    cart_items_count = sum(cart.values())
    request.session['cart_items_count'] = cart_items_count

    message = f"Товар добавлен в корзину, стало: {cart_items_count}."

    # Инициализируем список сообщений в сессии, если он еще не существует
    if 'messages' not in request.session:
        request.session['messages'] = []
    request.session['messages'].append(message)  # Добавляем сообщение в список

    # Перенаправляем на страницу указанную в параметре next или на главную
    # next скрыто в форме из какой вызывается POST запрос и равно url этой формы
    url = next if next else "/"
    return RedirectResponse(url=url, status_code=302)


@router.post("/update")
async def update_cart(request: Request, product_id: int = Form(...), quantity: int = Form(...)):
    """ Обновление корзины из формы корзины
    """
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if quantity <= 0:
        # Удаляем товар из корзины
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    request.session['cart_items_count'] = sum(cart.values())  # Обновляем количество товаров в корзине

    return RedirectResponse(url="/cart", status_code=302)


@router.post("/update/{product_id}")
async def update_item(request: Request, product_id: int, action: str = Form(...)):
    """ Обновление количества товара в корзине с главной страницы
        параметры:
        product_id - идентификатор товара
        action - действие, которое нужно выполнить
        increment - увеличить количество товара
        decrement - уменьшить количество товара
        add - добавить товар в корзину

        Возвращает количество товара в корзине
     """
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    current_quantity = cart.get(product_id_str, 0)

    if action == 'increment':
        cart[product_id_str] = current_quantity + 1
    elif action == 'decrement':
        cart[product_id_str] = current_quantity - 1
        if cart.get(product_id_str, 0) <= 0:
            del cart[product_id_str]
    elif action == 'add':
        cart[product_id_str] = 1
    else:
        return JSONResponse(content={"error": "Некорректное действие"}, status_code=400)

    request.session['cart'] = cart
    cart_items_count = sum(cart.values())
    request.session['cart_items_count'] = cart_items_count
    response = JSONResponse(content={"quantity": cart.get(product_id_str, 0), "cart_items_count": cart_items_count})
    return response


@router.post("/remove/{product_id}")
async def remove_item(request: Request, product_id: int):
    """Удаление товара из корзины
        параметры:
        product_id - идентификатор товара
        после удаления товара из корзины, возвращается на страницу корзины
    """
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)

    request.session['cart'] = cart
    request.session['cart_items_count'] = sum(cart.values())

    return RedirectResponse(url="/cart", status_code=302)


@router.post("/clear")
async def clear_cart(request: Request):
    """Очищает корзину
    :param request:
    :return:
    """
    cart = request.session.get('cart', {})
    cart.clear()

    request.session['cart'] = cart
    request.session['cart_items_count'] = sum(cart.values())

    return RedirectResponse(url="/cart", status_code=302)
