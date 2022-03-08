import re
import jwt

from hashlib import md5
from typing import Optional
from datetime import datetime
from src.main.user.utils import get_uuid
from pydantic import BaseModel, Field, validator
from src.main.user.exception import UserServerException
from src.main.util.time_utils import get_now_factory, get_now
from src.main.user.config import DEFAULT_TOKEN_EXPIRE_TIME, DEFAULT_JWT_SECRET


RE_PHONE_NUMBER = re.compile(r"^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$")
RE_EMAIL = re.compile(r"^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$")


class UserTokenInfo(BaseModel):
    userId: str = Field(..., description="user id")
    iat: int = Field(..., description="token生成时间")
    exp: int = Field(..., description="token过期时间")
    nickName: str = Field(..., description="用户昵称")
    account: str = Field(..., description="用户账号")


class UserInfoWriteAccess(BaseModel):
    nickName: str = Field(..., description="用户昵称")
    password: str = Field(..., description="用户密码")
    phone: str = Field(..., description="用户手机号")
    email: str = Field(..., description="用户邮箱")
    sign: Optional[str] = Field(default=None, description="用户个人签名")
    address: Optional[str] = Field(default=None, description="用户地址")


class User(UserInfoWriteAccess):
    userId: str = Field(default_factory=get_uuid, description="user id")
    account: str = Field(..., description="用户账号")
    isDelete: bool = Field(default=False, description="是否删除")
    updateTime: datetime = Field(default_factory=get_now_factory, description="更新时间")
    lastLoginTime: datetime = Field(default_factory=get_now_factory, description="上次登陆时间")

    @validator("phone")
    def validate_phone_number(cls, v):
        if RE_PHONE_NUMBER.search(v):
            return v
        raise UserServerException("error phone number: {}".format(v), error_code=400)

    @validator("email")
    def validate_email(cls, v):
        if RE_EMAIL.search(v):
            return v
        raise UserServerException("error email: {}".format(v), error_code=400)

    @classmethod
    def encrypt_password(cls, password: str) -> str:
        return md5(password.encode()).hexdigest()

    def get_token(self) -> str:
        now = get_now(return_type="timestamp")
        enc_data = UserTokenInfo(
            userId=self.userId, iat=now, exp=now + DEFAULT_TOKEN_EXPIRE_TIME * 24 * 60 * 60, nickName=self.nickName,
            account=self.account
        )
        return jwt.encode(enc_data.dict(), DEFAULT_JWT_SECRET).decode()

    @classmethod
    def decode_token(cls, token: str) -> UserTokenInfo:
        try:
            return UserTokenInfo(**jwt.decode(token, DEFAULT_JWT_SECRET, algorithms=["HS256"]))
        except jwt.exceptions.ExpiredSignatureError as _e:
            raise UserServerException("token过期", error_code=403)
        except Exception as _e:
            raise UserServerException("token is not valid, no authorization", error_code=403)

    def update_last_login_time(self):
        self.lastLoginTime = get_now_factory()


class UserRegisterRequestModel(BaseModel):
    nickName: str = Field(..., description="用户昵称")
    account: str = Field(..., description="用户账号")
    password: str = Field(..., description="用户密码")
    passwordRepeated: str = Field(..., description="重复输入的用户密码")
    phone: str = Field(..., description="用户手机号")
    email: str = Field(..., description="用户邮箱")
    address: Optional[str] = Field(default=None, description="用户地址")

    @validator("passwordRepeated")
    def validate_password_repeated_effectiveness(cls, value, values, **kwargs):
        if "password" in values and values["password"] == value:
            return value
        raise UserServerException("Inconsistent passwords!")


class UserLoginRequestModel(BaseModel):
    account: str = Field(..., description="用户账号")
    password: str = Field(..., description="用户密码")


class UserUpdatedInfo(UserInfoWriteAccess):
    nickName: Optional[str] = Field(default=None, description="用户昵称")
    password: Optional[str] = Field(default=None, description="用户密码")
    lastPassword: Optional[str] = Field(default=None, description="旧密码")
    phone: Optional[str] = Field(default=None, description="用户手机号")
    email: Optional[str] = Field(default=None, description="用户邮箱")
    sign: Optional[str] = Field(default=None, description="用户个人签名")
    address: Optional[str] = Field(default=None, description="用户地址")


class UserUpdateRequestModel(BaseModel):
    user: UserUpdatedInfo = Field(..., description="user信息")


class BaseResponseModel(BaseModel):
    message: str = Field(..., description="回馈信息")


class UserRegisterResponseModel(BaseResponseModel):
    userId: Optional[str] = Field(..., description="user id")
    accessToken: Optional[str] = Field(..., description="注册成功后的token")


class UserLoginResponseModel(BaseResponseModel):
    status: int = Field(..., description="登陆失败为0, 成功为1")
    accessToken: Optional[str] = Field(..., description="登录成功后的token")


class UserInfoShow(BaseModel):
    userId: str = Field(default_factory=get_uuid, description="user id")
    account: str = Field(..., description="用户账号")
    updateTime: str = Field(..., description="更新时间")
    lastLoginTime: str = Field(..., description="上次登陆时间")
    nickName: str = Field(..., description="用户昵称")
    phone: str = Field(..., description="用户手机号")
    email: str = Field(..., description="用户邮箱")
    sign: Optional[str] = Field(default=None, description="用户个人签名")
    address: Optional[str] = Field(default=None, description="用户地址")


class UserInfoResponseModel(BaseResponseModel):
    user: Optional[UserInfoShow] = Field(..., description="user信息")


class UserUpdateResponseModel(BaseResponseModel):
    userId: Optional[str] = Field(..., description="user id")


class UserLogOutResponseModel(BaseResponseModel):
    userId: Optional[str] = Field(..., description="user id")


class UserAuthorizationResponseModel(BaseModel):
    userId: Optional[str] = Field(..., description="user id")


if __name__ == '__main__':
    print(User(nickName="", account="", password="", phone="13761549452", email="1790927907@qq.com"))
