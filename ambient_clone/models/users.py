from dataclasses import dataclass
from typing import Union, cast

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from tinydb import Query

from ambient_clone.databases import UserTable
from ambient_clone.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: str
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


@dataclass
class Token:
    access_token: str
    token_type: str = "bearer"


class UserResult:
    is_ok: bool

    def ok(self) -> UserInDB:
        pass

    def err(self) -> "UserErr":
        pass


@dataclass
class UserOk(UserResult):
    value: UserInDB
    is_ok: True = True

    def ok(self) -> UserInDB:
        return self.value


@dataclass
class UserTokenOk(UserResult):
    token: Token
    is_ok: True = True


@dataclass
class UserErr(UserResult):
    message: str
    status_code: int = 400
    is_ok: False = False


def to_user(user: User) -> User:
    if type(user) == UserInDB:
        return User.model_validate(user)
    else:
        return user


def register_user(username: str, password: str) -> UserResult:
    q = Query()
    if UserTable.count(q.username == username) > 0:
        return UserErr("Username is already taken")

    user = UserInDB(
        **{"username": username, "hashed_password": pwd_context.hash(password)}
    )
    UserTable.insert(user.model_dump())

    return UserOk(user)


def find_user(username: str) -> UserResult:
    q = Query()
    user = UserTable.search(q.username == username)

    if len(user) == 0:
        return UserErr("not found", status_code=404)

    if len(user) > 1:
        raise "bug: username must be unique in db"

    return UserOk(UserInDB(**user[0]))


def verify_user(username: str, password: str) -> UserResult:
    user_result = find_user(username)
    if not user_result.is_ok:
        return UserErr("Incorrect username or password")

    user = user_result.ok()
    if not pwd_context.verify(password, user.hashed_password):
        return UserErr("Incorrect username or password")

    return UserOk(user)


def token(username: str, password: str) -> Union[UserTokenOk, UserErr]:
    user_result = verify_user(username, password)
    if not user_result.is_ok:
        return cast(user_result, UserErr)

    user = user_result.ok()

    return UserTokenOk(
        Token(jwt.encode({"username": user.username}, settings.jwt_secret))
    )


def decode_token(raw_token: str) -> UserResult:
    payload = jwt.decode(raw_token, settings.jwt_secret)
    return find_user(payload.get("username"))
