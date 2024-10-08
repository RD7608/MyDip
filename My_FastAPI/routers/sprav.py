from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import insert, select, update, delete
from sqlalchemy import exc
from typing import Annotated
from backend.db_depends import get_db
from models import Product, City, Order
from schemas import CreateProduct, UpdateProduct, CreateCity
from other import templates, get_current_user



router = APIRouter(prefix="/spr", tags=["spr"])


@router.get("/products", response_class=HTMLResponse)
async def get_products(request: Request, db: Session = Depends(get_db)):
    messages = request.session.get('messages', [])
    products = db.query(Product).all()
    cart_items_count = request.session.get ( 'cart_items_count' , 0 )
    user = get_current_user(request, db)
    context = {
        "request": request,
        "title": "Каталог",
        "messages": messages,
        "products": products,
        "cart_items_count": cart_items_count,
        "user": user
    }
    return templates.TemplateResponse("sprav/catalog.html", context)


@router.get("/product/{product_id}", response_class=HTMLResponse)
async def product_by_id(request: Request, product_id: int, db: Session = Depends(get_db)):
    cart_items_count = request.session.get ( 'cart_items_count' , 0 )
    # Получаем товар по id
    query = select(Product).where(Product.id == product_id)
    product = db.scalar(query)
    user = get_current_user(request, db)
    if product:
        context = {
            "request": request,
            "title": "Детали товара",
            "product": product,
            "cart_items_count": cart_items_count,
            "user": user
        }
        return templates.TemplateResponse("sprav/product.html", context)
    else:
        raise HTTPException(status_code=404, detail="Товар не найден")


@router.post("/create_product")
async def create_product(db: Annotated[Session, Depends(get_db)], product: CreateProduct):
    try:
        new_product = Product(name=product.name, description=product.description, image=product.image,
                              price=product.price, is_active=product.is_active, is_available=product.is_available)
        db.add(new_product)
        db.commit()  # Сохраняем изменения
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Товар добавлен"}
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка при добавлении товара: {str(e)}")


@router.put("/update_product")
async def update_product(db: Annotated[Session, Depends(get_db)], product_id: int, product: UpdateProduct):
    existing_product = db.scalar(select(Product).where(Product.id == product_id))
    if existing_product:
        db.execute(update(Product).where(Product.id == product_id).values(price=product.price,
                                                                          is_active=product.is_active,
                                                                          is_available=product.is_available))
        db.commit()
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Товар обновлен!"}
    else:
        raise HTTPException(status_code=404,
                            detail="Товар не найден")


@router.get("/cities")
async def get_cities(db: Session = Depends(get_db)):
    return db.query(City).all()


@router.post("/create_city")
async def create_city(db: Annotated[Session, Depends(get_db)], city: CreateCity):
    try:
        new_city = City(name=city.name, abbreviation=city.abbreviation)
        db.add(new_city)
        db.commit()
        return {"status_code": status.HTTP_200_OK,
                "transaction": "Город добавлен"}
    except exc.SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка при добавлении города: {str(e)}")
