from typing import Optional, Union
from typing_extensions import Literal
from pydantic import BaseModel, Field


class Novel(BaseModel):
    name: str = Field(..., description="小说名")
    briefIntroduction: Optional[str] = Field(default=None, description="简介")
    cover: Optional[str] = Field(default=None, description="封面, base64表示")
    author: str = Field(..., description="作者")
    status: Literal['serial', 'end'] = Field(default="serial", description="连载状态")
    score: float = Field(default=0, description="得分")


class NovelChapter(BaseModel):
    name: str = Field(..., description="小说章节名")
    content: str = Field(..., description="小说内容")


class Meta(BaseModel):
    version: str = Field(..., description="版本号")
    author: str = Field(..., description="作者")
    maintainer: str = Field(..., description="维护者")
    detectedSource: str = Field(..., description="来源")


class ParseResponse(BaseModel):
    message: str = Field(..., description="反馈")
    meta: Meta = Field(..., description="解析元数据")
    result: Optional[Union[Novel, NovelChapter]] = Field(default=None, description="解析后的数据")
    sourceType: Optional[Literal['Novel', 'NovelChapter']] = Field(default=None, description="数据的从属")
