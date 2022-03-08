import sqlalchemy

from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.functions import func
from src.main.novel.config import DATABASE_URL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

__all__ = [
    "novel_table",
    "novel_chapter_table",
    "novel_relation_table",
    "Base", "engine"
]

Base = declarative_base()
engine = sqlalchemy.create_engine(DATABASE_URL)


class TableNovel(Base):
    __tablename__ = 'Novel'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    uniqueId = sqlalchemy.Column(sqlalchemy.String(600), unique=True, nullable=False)
    channel = sqlalchemy.Column(sqlalchemy.String(600), index=True, nullable=False)
    briefIntroduction = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    cover = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String(1000), index=True, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False, index=True)
    score = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=False)
    novelType = sqlalchemy.Column(JSONB, nullable=False)
    extra = sqlalchemy.Column(JSONB, nullable=True)
    isDelete = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, server_default="0")
    createdBy = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    createTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=func.now())
    updateTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)


class TableNovelChapter(Base):
    __tablename__ = 'NovelChapter'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    uniqueId = sqlalchemy.Column(sqlalchemy.String(600), unique=True, nullable=False)
    chapterNum = sqlalchemy.Column(sqlalchemy.Integer, index=True, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)
    extra = sqlalchemy.Column(JSONB, nullable=True)
    isDelete = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, server_default="0")
    createdBy = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    createTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=func.now())
    updateTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)


class TableNovelRelation(Base):
    __tablename__ = 'NovelRelation'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    novelId = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False, index=True)
    novelChapterId = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False, index=True)
    createTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=func.now())
    updateTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)


novel_table: Table = TableNovel.__table__
novel_chapter_table: Table = TableNovelChapter.__table__
novel_relation_table: Table = TableNovelRelation.__table__
meta = sqlalchemy.MetaData()
meta.bind = engine
novel_table.metadata = meta
novel_chapter_table.metadata = meta
novel_relation_table.metadata = meta
