from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from entities.user import User
from entities.order import Order
from database.database import Session, engine
from fastapi.encoders import jsonable_encoder

from helpers.auth import require_jwt
from models.order import OrderModel

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

db_context = Session(bind=engine)


@order_router.get('/order/all')
async def get_all_orders(authorize: AuthJWT = Depends()):
    require_jwt(authorize)

    user = db_context.query(User).filter(User.username == authorize.get_jwt_subject()).first()
    if user.is_staff:
        orders = db_context.query(Order).all()

        return jsonable_encoder(orders)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@order_router.get('/order/my-orders')
async def user_orders(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = db_context.query(User).filter(User.username == authorize.get_jwt_subject()).first()
    orders = db_context.query(Order).filter(Order.user_id == user.id).all()

    return jsonable_encoder(orders)


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(model: OrderModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    current_user = authorize.get_jwt_subject()
    user = db_context.query(User).filter(User.username == current_user).first()
    order = Order(quantity=model.quantity, pizza_size=model.pizza_size)
    order.user = user
    db_context.add(order)
    db_context.commit()

    return jsonable_encoder({
        "pizza_size": order.pizza_size,
        "quantity": order.quantity
    })


@order_router.get('/order/get/{order_id}')
async def get_orders(order_id: int, authorize: AuthJWT = Depends()):
    require_jwt(authorize)

    user = db_context.query(User).filter(User.username == authorize.get_jwt_subject()).first()

    order = db_context.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if order.user_id == user.id or user.is_staff:
        return jsonable_encoder(order)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@order_router.put('/order/update/{order_id}')
async def update_order(model: OrderModel, order_id: int, authorize: AuthJWT = Depends()):
    require_jwt(authorize)
    user = db_context.query(User).filter(User.username == authorize.get_jwt_subject()).first()

    order = db_context.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if order.user_id == user.id:
        order.quantity = model.quantity
        order.pizza_size = model.pizza_size

        db_context.commit()

        return jsonable_encoder(order)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
