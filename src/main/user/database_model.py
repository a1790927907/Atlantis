import sqlalchemy

from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.functions import func
from src.main.user.config import DATABASE_URL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base


__all__ = (
    "Base",
    "engine",
    "user_table"
)

Base = declarative_base()
engine = sqlalchemy.create_engine(DATABASE_URL)


class TableUser(Base):
    __tablename__ = 'blogUser'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    userId = sqlalchemy.Column(sqlalchemy.String(600), unique=True, nullable=False)
    nickName = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False)
    account = sqlalchemy.Column(sqlalchemy.String(1000), nullable=False, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(600), index=True, nullable=False)
    sign = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    extra = sqlalchemy.Column(JSONB, nullable=True)
    isDelete = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, server_default=sqlalchemy.text(True))
    createTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=func.now())
    updateTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    lastLoginTime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)


user_table: Table = TableUser.__table__
meta = sqlalchemy.MetaData()
meta.bind = engine
user_table.metadata = meta
