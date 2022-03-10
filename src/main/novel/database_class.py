from sqlalchemy import select
from src.main.util.logger import logger
from typing import Callable, Optional, List
from sqlalchemy.dialects.postgresql.dml import Insert
from src.main.novel.model import Novel, NovelChapter, NovelTypeDBModel
from src.main.basicApplication.database.application import BaseDataBase
from src.main.novel.database_model import novel_table, novel_chapter_table, novel_relation_table, novel_type_table


class DataBase(BaseDataBase):
    def __init__(self, database_url: str, init_func: Callable, params: Optional[dict] = None):
        super().__init__(database_url, init_func, params)
        self.novel_table = novel_table
        self.novel_chapter_table = novel_chapter_table
        self.novel_relation_table = novel_relation_table
        self.novel_type_table = novel_type_table

    async def upsert_novel(self, novel: Novel):
        db = await self.get_db()
        data = novel.dict()
        insert_sql: Insert = Insert(self.novel_table, inline=True).values(data)
        insert_sql = insert_sql.on_conflict_do_update(
            index_elements=["uniqueId"],
            set_=data
        )
        await db.execute(insert_sql)
        logger.info("success upsert novel, uid: {}, name: {]".format(novel.uniqueId, novel.name))

    async def upsert_novel_type(self, novel_type_for_db: NovelTypeDBModel):
        db = await self.get_db()
        data = novel_type_for_db.dict()
        insert_sql: Insert = Insert(self.novel_type_table, inline=True).values(data)
        await db.execute(insert_sql)
        logger.info("success upsert novel type, novel type info: {}".format(data))

    async def upsert_novel_chapter(self, novel_chapter: NovelChapter):
        db = await self.get_db()
        data = novel_chapter.dict()
        insert_sql: Insert = Insert(self.novel_chapter_table, inline=True).values(data)
        insert_sql = insert_sql.on_conflict_do_update(
            index_elements=["uniqueId"],
            set_=data
        )
        await db.execute(insert_sql)
        logger.info("success upsert novel chapter, uid: {}, name: {}, chapter num: {}".format(
            novel_chapter.uniqueId, novel_chapter.name, novel_chapter.chapterNum
        ))

    async def get_novel(self, uid: str):
        db = await self.get_db()
        query = self.novel_table.select().filter_by(uniqueId=uid)
        return await db.fetch_one(query)

    async def get_novel_type(self, novel_id: str) -> list:
        db = await self.get_db()
        query = self.novel_type_table.select().filter_by(novelId=novel_id)
        return await db.fetch_all(query)

    async def get_novel_chapter(self, uid: str):
        db = await self.get_db()
        query = self.novel_chapter_table.select().filter_by(uniqueId=uid)
        return await db.fetch_one(query)

    async def bulk_get_novel_chapter(self, uid_list: List[str]) -> list:
        db = await self.get_db()
        query = self.novel_chapter_table.select().filter(
            self.novel_chapter_table.c.uniqueId.in_(uid_list)
        ).order_by(self.novel_chapter_table.chapterNum.asc())
        return await db.fetch_all(query)

    async def get_novel_chapter_by_novel(self, novel_id: str) -> list:
        db = await self.get_db()
        query = select([self.novel_relation_table.c.novelChapterId]).filter(
            self.novel_relation_table.c.novelId == novel_id
        )
        _novel_chapter_ids = await db.fetch_all(query)
        novel_chapter_ids = [
            dict(novel_chapter_obj)["novelChapterId"]
            for novel_chapter_obj in _novel_chapter_ids
        ]
        novel_chapter_ids = list(set(novel_chapter_ids))
        return await self.bulk_get_novel_chapter(novel_chapter_ids)
