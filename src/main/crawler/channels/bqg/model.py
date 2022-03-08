from typing import Dict
from pydantic import BaseModel, Field


class NovelTypeDetail(BaseModel):
    cn: str = Field(..., description="中文名")
    code: int = Field(..., description="对应的code")


class NovelTypeMapper(BaseModel):
    detail: Dict[str, NovelTypeDetail] = Field(..., description="novel 类型对应数据库中的类型")
