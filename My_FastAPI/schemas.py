from pydantic import BaseModel
from models import Product


class CreateCity(BaseModel):
    name: str
    abbreviation: str


class CreateProduct(BaseModel):
    name: str
    description: str
    image: str
    price: float = None
    is_active: bool = True
    is_available: bool = False


class UpdateProduct(BaseModel):
    price: float
    is_active: bool
    is_available: bool


class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool = True
    firstname: str = None
    lastname: str = None
    customer_name: str = None
    city: int = None
    address: str = None
    phone: str = None

    class Config:
        from_attributes = True


class UpdateUser(BaseModel):
    email: str
    password: str = None
    firstname: str
    lastname: str
    customer_name: str
    city: int
    address: str
    phone: str


class CreateOrder(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    city: int
    address: str
    delivery_date: str = None
    items: list = []
    is_new: bool = True
    is_confirmed: bool = False
    is_delivered: bool = False
    is_canceled: bool = False


class UpdateOrder(BaseModel):
    customer_name: str
    delivery_date: str
    items: list
