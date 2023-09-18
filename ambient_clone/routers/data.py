from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, status, Depends
from tinyflux import Point, TagQuery

from ambient_clone.databases import tsdb
from ambient_clone.models.data import Datum, command_to_point, json_to_point
from ambient_clone.models.users import decode_token
from ambient_clone.routers.auth import oauth2_scheme

router = APIRouter(tags=["data"])


@router.get("/data")
async def data(token: Annotated[str, Depends(oauth2_scheme)]) -> list[Datum]:
    user_result = decode_token(token)

    tag = TagQuery()
    d = tsdb.search(tag["@user"] == user_result.ok().username)

    def p2d(p: Point) -> Datum:
        print(p)
        timestamp = "-" if p.time is None else p.time
        return Datum.model_validate({**p.fields, **{"timestamp": timestamp, "measurement": p.measurement}})

    return list(map(p2d, d))


@router.post("/data",
             openapi_extra={
                 "requestBody": {
                     "content": {
                         "text/plain": {"example": "m,tag=tag1 field1=1,field2=2.3 1640995200000000000"},
                         "application/json": {
                             "schema": Datum.model_json_schema()
                         }},
                     "required": True,
                 },
             },
             status_code=status.HTTP_204_NO_CONTENT)
async def push(token: Annotated[str, Depends(oauth2_scheme)], req: Request):
    user_result = decode_token(token)
    content_type = req.headers['content-type']
    body = await req.body()
    p: Point
    match content_type:
        case "application/json":
            p = json_to_point(Datum.model_validate_json(body))
        case "text/plain":
            p = command_to_point(body.decode('utf-8'))
        case _:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    print(p)
    p.tags["@user"] = user_result.ok().username

    tsdb.insert(p)
