from pydantic import BaseModel, EmailStr, BaseSettings
from models import User
from typing import Optional

# import os
# from dotenv import load_dotenv
#
# load_dotenv()  # .env fayldan o‘qish

class Settings(BaseSettings):
    authjwt_secret_key: str     #= os.getenv("AUTHJWT_SECRET_KEY")

    class Config:
        env_file = ".env"


class LoginModel(BaseModel):

    username: Optional[str]
    password: str
    email:Optional[str]


class SignupModel(BaseModel):

    id: Optional[int]
    username: str
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_staff: Optional[bool] = False


class OrderModel(BaseModel):

    id: Optional[int]
    quantity: int
    status: Optional[str] = "PENDING"
    product_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                'quantity': 2,
                "product": 7
            }
        }

class OrderStatusModel(BaseModel):

    order: Optional[str] = "PENDING"
    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                'status': "PENDING",
            }
        }


class ProductModel(BaseModel):

    name: str
    price: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                "name": "Palov",
                "price": 40000
            }
        }