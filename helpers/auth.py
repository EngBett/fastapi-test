from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT


def require_jwt(authorize: AuthJWT):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
