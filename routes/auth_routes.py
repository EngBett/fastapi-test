from fastapi import APIRouter, HTTPException, status, Depends
from database.database import Session, engine
from entities.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

from models.login import LoginModel
from models.signup import SignUpModel

auth_router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

db_context = Session(bind=engine)


@auth_router.get('/')
async def hello(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return {"message": "hello world"}


@auth_router.post('/signup')
async def signup(sign_up_model: SignUpModel):
    db_email = db_context.query(User).filter(User.email == sign_up_model.email).first()
    if db_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email exists"
        )

    db_username = db_context.query(User).filter(User.username == sign_up_model.username).first()
    if db_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that username exists"
        )

    new_user = User(
        username=sign_up_model.username,
        email=sign_up_model.email,
        password=generate_password_hash(sign_up_model.password),
        is_active=sign_up_model.is_active,
        is_staff=sign_up_model.is_staff
    )

    db_context.add(new_user)
    db_context.commit()

    return new_user


@auth_router.post('/login')
async def login(login_model: LoginModel, authorize: AuthJWT = Depends()):
    db_user = db_context.query(User).filter(User.username == login_model.username).first()
    if db_user and check_password_hash(db_user.password, login_model.password):
        access_token = authorize.create_access_token(subject=db_user.username)
        refresh = authorize.create_refresh_token(subject=db_user.username)

        response = {
            "access_token": access_token,
            "refresh_token": refresh
        }

        return jsonable_encoder(response)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Authentication failed"
    )


@auth_router.get('/refresh')
async def refresh_token(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_refresh_token_required()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    current_user = authorize.get_jwt_subject()

    access_token = authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access": access_token})
