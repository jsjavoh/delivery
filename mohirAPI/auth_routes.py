import datetime

from fastapi import APIRouter, Body, Depends, status, HTTPException
from typing import Annotated

from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from sqlalchemy.sql.functions import current_user

from schemas import SignupModel, LoginModel
from sqlalchemy.orm import Session
from database import get_db
from models import User, Order
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
router = APIRouter(
    prefix='/auth'
)

@router.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return {
        'message':'Siz auth route sahifadasiz!'
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def root(
    user: Annotated[SignupModel, Body()],
    db: Session = Depends(get_db),
):
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu email dbda mavjud!")

    db_username = db.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu username dbda mavjud!")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Yangi ma'lumotlarni yangilash

    return {
        "message": "Foydalanuvchi muvaffaqiyatli ro‘yxatdan o‘tdi",
        "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    }

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user: Annotated[LoginModel, Body()],
    db: Session = Depends(get_db),
    Authorise: AuthJWT = Depends(),
):
    # db_user = db.query(User).filter(User.username == user.username).first()
    access_lifetime = datetime.timedelta(minutes=1)
    refresh_lifetime = datetime.timedelta(days=3)
    db_user = db.query(User).filter(or_(User.username == user.username, User.email == user.email)).first()

    if not db_user or not check_password_hash(db_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username yoki password xato!")
    access_token = Authorise.create_access_token(subject=db_user.username, expires_time=access_lifetime)
    refresh_token = Authorise.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)
    return {
        'access_token':access_token,
        'refresh_token':refresh_token
    }


@router.get("/login/refresh")
async def refresh(
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):

    try:
        Authorize.jwt_refresh_token_required()
        access_lifetime = datetime.timedelta(minutes=1)
        current_user = Authorize.get_jwt_subject()

        db_user = db.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")

        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        response_model = {
            'success': True,
            'code':200,
            'message':"create a new access token!",
            'data':{
                'access token' : new_access_token,
            },
        }
        return response_model

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!")


@router.get("/auth-order")
async def auth_order(
    db: Session = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    username = authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == username).first()
    orders = user.order

    return jsonable_encoder(orders)

@router.