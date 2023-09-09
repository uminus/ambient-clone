from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status

from ambient_clone.models.users import User, decode_token, register_user, to_user
from ambient_clone.routers.auth import oauth2_scheme

router = APIRouter(tags=["users"])


@router.get("/user")
async def user_me(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_result = decode_token(token)
    if user_result.is_ok:
        return user_result.ok()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/register")
async def register(
    username: Annotated[str, Form()], password: Annotated[str, Form()]
) -> User:
    user_result = register_user(username, password)
    if user_result.is_ok:
        return to_user(user_result.ok())
    else:
        e = user_result.err()
        raise HTTPException(status_code=e.status_code, detail=e.message)
