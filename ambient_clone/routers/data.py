from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import HTTP_204_NO_CONTENT
from tinyflux import Point, TagQuery

from ambient_clone.databases import Measurement
from ambient_clone.models.data import Datum
from ambient_clone.models.users import decode_token
from ambient_clone.routers.auth import oauth2_scheme

router = APIRouter(tags=["data"])


@router.get("/data")
async def data(token: Annotated[str, Depends(oauth2_scheme)]) -> list[Datum]:
    user_result = decode_token(token)

    tag = TagQuery()
    d = Measurement.search(tag["@user"] == user_result.ok().username)

    def p2d(p: Point) -> Datum:
        timestamp = "-" if p.time is None else p.time
        return Datum.model_validate({**p.fields, **{"timestamp": timestamp}})

    return list(map(p2d, d))


@router.post("/data", status_code=HTTP_204_NO_CONTENT)
async def push(token: Annotated[str, Depends(oauth2_scheme)]):
    user_result = decode_token(token)

    Measurement.insert(
        Point(
            time=datetime.now(timezone.utc),
            fields={"a": datetime.now(timezone.utc).timestamp()},
            tags={"@user": user_result.ok().username},
        )
    )
