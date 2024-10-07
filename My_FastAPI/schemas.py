from pydantic import BaseModel, EmailStr
from datetime import date


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
    email: EmailStr
    password: str
    is_active: bool = True
    firstname: str = None
    lastname: str = None
    customer_name: str = None
    city: int = None
    address: str = None
    phone: str = None


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
    customer_email: EmailStr
    customer_phone: str
    city: int
    address: str
    delivery_date: date


class UpdateOrder(BaseModel):
    customer_name: str
    delivery_date: str
