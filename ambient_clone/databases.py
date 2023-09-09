from tinydb import TinyDB
from tinydb.storages import MemoryStorage as TinyDBMemoryStorage
from tinyflux import TinyFlux
from tinyflux.storages import MemoryStorage as TinyFluxDBMemoryStrage

from ambient_clone.settings import settings

if settings.db_file is None:
    db = TinyDB(storage=TinyDBMemoryStorage)
else:
    db = TinyDB(settings.db_file)

UserTable = db.table("user")

if settings.tsdb_file is None:
    tsdb = TinyFlux(storage=TinyFluxDBMemoryStrage)
else:
    tsdb = TinyFlux(settings.tsdb_file)

Measurement = tsdb.measurement("tsdb")
