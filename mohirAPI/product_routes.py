from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Body, Path
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProductModel
from models import User, Product, Order


router = APIRouter(
    prefix="/product"
)

@router.get("/")
async def welcome(
    authorize: AuthJWT = Depends()
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token!")
    return {
        "message":"Siz producr route'da sahifasidasiz!"
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def product_create(
    product: Annotated[ProductModel, Body()],
    authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token!")

    user = authorize.get_jwt_subject()
    current_user = db.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        new_product = Product(
            name = product.name,
            price = product.price
        )
        db.add(new_product)
        db.commit()
        data = {
            "success":True,
            "code":201,
            "message":"Product is created",
            "data":{
                "id":new_product.id,
                "name":new_product.name,
                "price":new_product.price,
            },
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser")



@router.get("/list")
async def list_product(
    db: Session = Depends(get_db),
    authorize: AuthJWT = Depends()
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token!")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        products = db.query(Product).all()

        data = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]
        return jsonable_encoder(data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser!")


@router.get("/{id}")
async def product_id(
    id: Annotated[int, Path()],
    db: Session = Depends(get_db),
    authorize: AuthJWT = Depends()
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token!")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if user.is_staff:

        product = db.query(Product).filter(Product.id == id).first()
        if product:
            data ={
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }

            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser!")


@router.delete("/{id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def product_delete(
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
        product = db.query(Product).filter(Product.id == id).first()
        if product:
            db.delete(product)
            db.commit()

            response_data = {
                "status": True,
                "code": 204,
                "message":f"Product ID={id} deleted",
                "data":None
            }
            return jsonable_encoder(response_data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser")


@router.put("/{id}/update")
async def product_update(
    id: Annotated[int, Path()],
    update_data: Annotated[ProductModel, Body()],
    db: Session = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    current_user = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_staff:
        product = db.query(Product).filter(Product.id == id).first()
        if product:
            allowed_fields = {'name','price'}
            for key, value in update_data.dict(exclude_unset = True).items():  # exclude_unset=True — foydalanuvchi yuborgan maydonlarni topadi.
                setattr(product,key,value) # product obyektida shu atributlarni yangilaydi.

            db.commit()
            response_data = {
                "status": True,
                "code": 200,
                "message":f"Product ID={id} update",
                "data": {
                    "name":product.name,
                    'price':product.price
                }
            }
            return jsonable_encoder(response_data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not Superuser")
