from contextlib import asynccontextmanager
from typing import AsyncGenerator

from databases import Database
from litestar import Litestar


def get_db_lifespan_manager(db_url):
    database = Database(str(db_url))

    @asynccontextmanager
    async def db_lifespan(app: Litestar) -> AsyncGenerator[None, None]:
        await database.connect()
        yield
        await database.disconnect()

    return db_lifespan
