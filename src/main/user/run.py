import uvicorn

from src.main.util.logger import logger
from fastapi import FastAPI, Request, Cookie
from src.main.util.time_utils import get_now
from src.main.user.config import DATABASE_URL
from src.main.user.database_class import DataBase
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from src.main.user.exception import UserServerException
from src.main.user.utils import check_request_validation, create_tables
from src.main.util.data_process_utils import format_dict_to_be_json_serializable
from src.main.user.model import UserRegisterResponseModel, UserRegisterRequestModel, User, \
    UserLoginRequestModel, UserLoginResponseModel, UserInfoResponseModel, UserUpdateRequestModel, \
    UserUpdateResponseModel, UserLogOutResponseModel, UserAuthorizationResponseModel

db = DataBase(database_url=DATABASE_URL, init_func=create_tables)
app = FastAPI(docs_url="/user/docs", redoc_url="/user/reDocs", description="user API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_token(request: Request, call_next):
    url_path_without_token = ["/user/register", "/user/login"]
    try:
        if request.url.path not in url_path_without_token:
            token = request.cookies.get("auth")
            token_info = User.decode_token(token)
            if token_info.exp <= get_now(return_type="timestamp"):
                raise UserServerException("token is overdue", error_code=403)
        response = await call_next(request)
        return response
    except UserServerException as e:
        response = JSONResponse(content={
            "message": e.message
        }, status_code=e.error_code)
        response.delete_cookie(key="auth")
        return response


@app.get(
    "/user/authorization", description="检测登录状态的", response_model=UserAuthorizationResponseModel,
    include_in_schema=False
)
async def authorize(auth: str = Cookie(...)):
    response = JSONResponse(content={
        "userId": User.decode_token(auth).userId
    })
    return response


@app.post("/user/register", description="注册用户", response_model=UserRegisterResponseModel)
async def register_user(
        register_info: UserRegisterRequestModel, response: Response
):
    try:
        password = User.encrypt_password(password=register_info.password)
        if await db.get_user_by_account(account=register_info.account):
            raise UserServerException("account: {} already exists".format(register_info.account))
        user = User(
            nickName=register_info.nickName, account=register_info.account, password=password,
            phone=register_info.phone, email=register_info.email, address=register_info.address
        )
        await db.upsert_user(user)
        token = user.get_token()
        response_message = {
            "message": "ok",
            "userId": user.userId,
            "accessToken": token
        }
        response.set_cookie(key="auth", value=token, httponly=True)
        return response_message
    except UserServerException as e:
        response_message = {
            "message": e.message,
            "userId": None,
            "accessToken": None
        }
        response.status_code = e.error_code
        return response_message
    except Exception as e:
        response_message = {
            "message": repr(e),
            "userId": None,
            "accessToken": None
        }
        response.status_code = 500
        return response_message


@app.post("/user/login", description="登录", response_model=UserLoginResponseModel)
async def login(
        request: Request,
        response: Response,
        user_info: UserLoginRequestModel
):
    try:
        await check_request_validation(user_info.dict(), dict(request.headers))
        user = await db.get_user_by_account(user_info.account)
        if not user:
            raise UserServerException("account: {} not found".format(user_info.account), error_code=404)
        password = user_info.password
        user = User(**dict(user))
        if password != user.password:
            raise UserServerException("password error!", error_code=403)
        user.update_last_login_time()
        await db.upsert_user(user)
        token = user.get_token()
        response_message = {
            "message": "success",
            "status": 1,
            "accessToken": token
        }
        response.set_cookie(key="auth", value=token, httponly=True)
        return response_message
    except Exception as e:
        response_message = {
            "message": e.message if isinstance(e, UserServerException) else repr(e),
            "status": 0,
            "accessToken": None
        }
        response.status_code = e.error_code if isinstance(e, UserServerException) else 500
        return response_message


@app.get("/user/logout", response_model=UserLogOutResponseModel, description="退出登录")
async def logout(response: Response, auth: str = Cookie(...)):
    token_info = User.decode_token(auth)
    response_message = {
        "message": "ok",
        "userId": token_info.userId
    }
    response.delete_cookie(key="auth")
    return response_message


@app.get("/user/info", response_model=UserInfoResponseModel, description="获取user信息")
async def get_user_info(response: Response, auth: str = Cookie(...)):
    try:
        token_info = User.decode_token(auth)
        user = await db.get_user_by_user_id(token_info.userId)
        if not user:
            raise UserServerException("userId: {} not found".format(user), error_code=404)
        response_message = {
            "message": "ok",
            "user": format_dict_to_be_json_serializable(dict(user))
        }
        return response_message
    except Exception as e:
        logger.exception(e)
        response_message = {
            "message": e.message if isinstance(e, UserServerException) else repr(e),
            "user": None
        }
        response.status_code = e.error_code if isinstance(e, UserServerException) else 500
        return response_message


@app.post("/user/update", response_model=UserUpdateResponseModel, description="更新用户信息")
async def update_user_info(
        response: Response,
        user_info: UserUpdateRequestModel,
        auth: str = Cookie(...)
):
    try:
        token_info = User.decode_token(auth)
        user = await db.get_user_by_user_id(token_info.userId)
        if not user:
            raise UserServerException("userId: {} not found".format(token_info.userId), error_code=404)
        user = dict(user)
        if User.encrypt_password(user_info.user.lastPassword) != user["password"]:
            raise UserServerException("password validate error", error_code=403)
        _user_info = user_info.user.dict()
        user_info_updated = {
            key: value for key, value in _user_info.items() if value
        }
        await db.upsert_user(User(**{
            **dict(user),
            **user_info_updated
        }))
        return {
            "message": "success"
        }
    except Exception as e:
        logger.exception(e)
        response.status_code = e.error_code if isinstance(e, UserServerException) else 500
        return {
            "message": e.message if isinstance(e, UserServerException) else repr(e)
        }


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
