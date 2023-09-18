import re
from datetime import datetime
from typing import Iterator, Match, Union, Optional

from pydantic import BaseModel, Extra
from tinyflux import Point


class Datum(BaseModel):
    measurement: Optional[str] = "measurement"
    timestamp: Optional[datetime] = datetime.utcnow()
    fields: Optional[dict[str, Union[int, float, None]]] = None
    tags: Optional[dict[str, str]] = None

    class Config:
        extra = Extra.allow


command_pattern = re.compile(r'^(?P<measurement>\w+)(?:,(?P<tags>.+))? (?P<fields>\S+) (?P<timestamp>\d+)$')
kv_pattern = re.compile(r'(?P<key>\w+)=(?:(?P<number>\d+(?:\.\d+)?)|(?:"(?P<quoted_str>[^"]*)"|(?P<str>\w+)))(?:,|$)')


def __to_dict(it: Iterator[Match[str]], str_only: bool = False) -> dict[str, Union[str, int, float, None]]:
    d = dict()
    for m in it:
        g = m.groupdict()
        v = None
        if g["str"] is not None:
            v = g["str"]
        elif g["quoted_str"] is not None:
            v = g["quoted_str"]
        elif g["number"] is not None:
            if str_only:
                v = g["number"]
            else:
                v = float(g["number"])

        if v is not None:
            d[g["key"]] = v

    return d


def command_to_point(command: str) -> Point:
    """Converts InfluxDB cli write command format string to Point."""

    m = command_pattern.match(command).groupdict()
    return Point(
        measurement=m["measurement"],
        time=datetime.utcfromtimestamp(int(m["timestamp"]) / 1000000000),  # nanoseconds to seconds
        tags=__to_dict(kv_pattern.finditer(m["tags"]), str_only=True),
        fields=__to_dict(kv_pattern.finditer(m["fields"])),
    )


def json_to_point(datum: Datum) -> Point:
    return Point(
        measurement=datum.measurement,
        time=datum.timestamp,
        tags=datum.tags,
        fields=datum.fields,
    )
