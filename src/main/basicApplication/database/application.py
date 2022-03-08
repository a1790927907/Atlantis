import databases

from typing import Callable, Optional
from src.main.util.logger import logger
from sqlalchemy_utils import database_exists, create_database


class BaseDataBase:
    def __init__(self, database_url: str, init_func: Callable, params: Optional[dict] = None):
        if not database_exists(database_url):
            create_database(database_url)
            logger.info("success create database: {}".format(database_url))
        init_func(**(params or {}))
        self.db = databases.Database(database_url)

    async def connect(self):
        await self.db.connect()

    async def disconnect(self):
        await self.db.disconnect()

    async def get_db(self):
        if not self.db.is_connected:
            await self.connect()
        return self.db
