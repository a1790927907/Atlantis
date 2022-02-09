import databases

from src.main.user.model import User
from src.main.util.logger import logger
from src.main.user.database_model import user_table
from sqlalchemy.dialects.postgresql.dml import Insert
from src.main.user.exception import UserServerException
from sqlalchemy_utils import create_database, database_exists


class DataBase:
    def __init__(self, database_url: str):
        if not database_exists(database_url):
            create_database(database_url)
            logger.info("success create database: {}".format(database_url))
        self.db = databases.Database(database_url)
        self.user_table = user_table

    async def connect(self):
        await self.db.connect()

    async def disconnect(self):
        await self.db.disconnect()

    async def get_db(self):
        if not self.db.is_connected:
            await self.connect()
        return self.db

    async def upsert_user(self, user_info: User):
        db = await self.get_db()
        insert_sql: Insert = Insert(self.user_table, inline=True).values(user_info.dict())
        insert_sql = insert_sql.on_conflict_do_update(
            index_elements=["userId"],
            set_=user_info.dict()
        )
        await db.execute(insert_sql)
        logger.info("success insert user, user id: {}".format(user_info.userId))

    async def get_user_by_user_id(self, user_id: str):
        db = await self.get_db()
        query = self.user_table.select().filter_by(userId=user_id, isDelete=False)
        return await db.fetch_one(query)

    async def get_user_by_account(self, account: str):
        db = await self.get_db()
        query = self.user_table.select().filter_by(account=account)
        return await db.fetch_one(query)

    async def delete_user_by_user_id(self, user_id: str):
        db = await self.get_db()
        user = await self.get_user_by_user_id(user_id)
        if not user:
            raise UserServerException("user id: {} not found".format(user_id), error_code=404)
        sql: Insert = Insert(self.user_table, inline=True).values(dict(user))
        sql = sql.on_conflict_do_update(
            index_elements=["userId"],
            set_={
                **dict(user),
                "isDelete": True
            }
        )
        await db.execute(sql)
        logger.info("success delete user, user id: {}".format(user_id))
