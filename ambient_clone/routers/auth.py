from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ambient_clone.models.users import token

router = APIRouter(tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    token_result = token(form_data.username, form_data.username)

    if token_result.is_ok:
        return token_result.token
    else:
        raise HTTPException(
            status_code=token_result.status_code,
            detail=token_result.message,
        )
