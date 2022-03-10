from typing import Optional
from datetime import datetime
from typing_extensions import Literal
from pydantic import BaseModel, Field
from src.main.util.generator_util import get_uuid
from src.main.util.time_utils import get_now_factory


class Meta(BaseModel):
    detectedSource: Optional[str] = Field(default=None, description="来源")


class Novel(BaseModel):
    name: str = Field(..., description="小说名")
    uniqueId: str = Field(default_factory=get_uuid, description="unique id")
    channel: Literal['xbiquge.la'] = Field(..., description="来源渠道")
    briefIntroduction: Optional[str] = Field(default=None, description="简介")
    cover: Optional[str] = Field(default=None, description="封面, base64表示")
    author: str = Field(..., description="作者")
    score: float = Field(..., description="得分")
    status: Literal['serial', 'end'] = Field(default="serial", description="连载状态")
    meta: Meta = Field(default=Meta(), description="源数据")
    createdBy: str = Field(default=..., description="创建者ID")
    updateTime: datetime = Field(default_factory=get_now_factory, description="更新时间")
    isDelete: bool = Field(default=False, description="是否删除")


class NovelTypeDBModel(BaseModel):
    novelTypeCode: int = Field(..., description="小说类型的code")
    novelTypeName: str = Field(..., description="小说类型的名称")
    novelId: str = Field(..., description="小说ID")


class NovelChapter(BaseModel):
    name: str = Field(..., description="小说章节名")
    uniqueId: str = Field(default_factory=get_uuid, description="unique id")
    chapterNum: int = Field(..., description="章节号")
    content: str = Field(..., description="小说内容")
    meta: Meta = Field(default=Meta(), description="源数据")
    createdBy: str = Field(default=..., description="创建者ID")
    updateTime: datetime = Field(default_factory=get_now_factory, description="更新时间")
    isDelete: bool = Field(default=False, description="是否删除")


class NovelRelation(BaseModel):
    novelId: str = Field(..., description="小说实体ID")
    novelChapterId: str = Field(..., description="小说章节ID")
    updateTime: datetime = Field(default_factory=get_now_factory, description="更新时间")


class NovelType(BaseModel):
    code: str = Field(..., description="类型的code")
    cn: str = Field(..., description="类型的名称")
