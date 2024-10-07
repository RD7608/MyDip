from pydantic import BaseModel, EmailStr
from datetime import date

from pydantic.v1 import validator


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
    username: str
    firstname: str
    lastname: str
    customer_name: str
    city_id: int
    address: str
    phone: str

    @validator('city_id', pre=True)
    def validate_city_id(cls, value):
        if not isinstance(value, int):
            raise ValueError('City ID must be an integer.')
        return value

    @validator('username', 'firstname', 'lastname', 'customer_name', 'address', 'phone', always=True)
    def check_none(cls, v):
        if v is None:
            raise ValueError('Value cannot be empty or null.')
        return v

    class Config:
        json_schema_extra = {
            'example': {
                'username': 'johndoe',
                'firstname': 'John',
                'lastname': 'Doe',
                'customer_name': 'John Doe',
                'city_id': 1,
                'address': '123 Main Street',
                'phone': '+1234567890'
            },
        }


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
