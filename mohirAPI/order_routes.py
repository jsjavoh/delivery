from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from fastapi_jwt_auth import AuthJWT
from jwt.utils import raw_to_der_signature

from models import User, Order, Product
from database import get_db
from sqlalchemy.orm import Session
from schemas import OrderModel, OrderStatusModel
from fastapi.encoders import jsonable_encoder
from typing import Annotated


router = APIRouter(
    prefix='/order'
)


@router.get('/')
async def welcome(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return {
        "message":"Siz Order route sahifasidasiz!"
    }


@router.post('/make', status_code=status.HTTP_201_CREATED)
async def make_order(
    order: Annotated[OrderModel, Body(...)],
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token!")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()
    # product = db.query(Product).filter(Product.id == order.product_id).first()

    new_order = Order(
        quantity=order.quantity,
        user_id=user.id,
        product_id=order.product_id
    )

    db.add(new_order)
    db.commit()


    response = {
        "id":new_order.id,
        'quantity':new_order.quantity,
        "status":new_order.status.value,
        "user":{
            "username":new_order.user.username,
            "email":new_order.user.email
        },
        "product":{
            "name":new_order.product.name,
            "price":new_order.product.price
        },
    }
    return jsonable_encoder(response)


@router.get("/list")
async def order_list(
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        orders = db.query(Order).all()
        data = [
            {
                "id":order.id,
                "user":{
                    "id":order.user.id,
                    "username":order.user.username,
                    "email":order.user.email
                },
                "product":{
                    "name":order.product.name,
                    "price":order.product.price
                },
                "quantity":order.quantity,
                "status":order.status.value
            }
            for order in orders
        ]
        return jsonable_encoder(data)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not superuser")


@router.get("/{id}")
async def order_id(
    id: Annotated[int, Path()],
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
 
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        order = db.query(Order).filter(Order.id == id).first()
        data = {
            "id": id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product":{
                "name":order.product.name,
                "price":order.product.price
            },
            "quantity": order.quantity,
            "status": order.status
        }
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser")
