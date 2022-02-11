import uvicorn

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, Cookie
from src.main.util.time_utils import get_now
from src.main.user.config import DATABASE_URL
from src.main.user.database_class import DataBase
from src.main.user.exception import UserServerException
from src.main.user.model import UserRegisterResponseModel, UserRegisterRequestModel, User, \
    UserLoginRequestModel, UserLoginResponseModel, UserInfoResponseModel, UserUpdateRequestModel, \
    UserUpdateResponseModel, UserLogOutResponseModel, UserAuthorizationResponseModel

db = DataBase(database_url=DATABASE_URL)
app = FastAPI(docs_url="/user/docs", redoc_url="/user/reDocs", description="user API")


@app.middleware("http")
async def check_token(request: Request, call_next):
    url_path_without_token = ["/user/register", "/user/login"]
    try:
        token = request.cookies.get("auth")
        token_info = User.decode_token(token)
        if token_info.exp <= get_now(return_type="timestamp") and request.url.path not in url_path_without_token:
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
    return JSONResponse(content={
        "userId": User.decode_token(auth).userId
    })


@app.post("/user/register", description="注册用户", response_model=UserRegisterResponseModel)
async def register_user(
        register_info: UserRegisterRequestModel
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
        response = JSONResponse(content={
            "message": "ok",
            "userId": user.userId
        })
        response.set_cookie(key="auth", value=user.get_token())
        return response
    except UserServerException as e:
        return JSONResponse(content={
            "message": e.message,
            "userId": None
        }, status_code=e.error_code)
    except Exception as e:
        return JSONResponse(content={
            "message": repr(e),
            "userId": None
        }, status_code=500)


@app.post("/user/login", description="登录", response_model=UserLoginResponseModel)
async def login(
        user_info: UserLoginRequestModel
):
    try:
        user = await db.get_user_by_account(user_info.account)
        if not user:
            raise UserServerException("account: {} not found".format(user_info.account), error_code=404)
        password = User.encrypt_password(user_info.password)
        user = User(**dict(user))
        if password != user.password:
            raise UserServerException("password error!", error_code=403)
        user.update_last_login_time()
        await db.upsert_user(user)
        response = JSONResponse(content={
            "message": "success",
            "status": 1
        })
        response.set_cookie(key="auth", value=user.get_token())
        return response
    except Exception as e:
        return JSONResponse(content={
            "message": e.message if isinstance(e, UserServerException) else repr(e),
            "status": 0
        }, status_code=e.error_code if isinstance(e, UserServerException) else 500)


@app.get("/user/logout", response_model=UserLogOutResponseModel, description="退出登录")
async def logout(auth: str = Cookie(...)):
    token_info = User.decode_token(auth)
    response = JSONResponse(content={
        "message": "ok",
        "userId": token_info.userId
    })
    response.delete_cookie(key="auth")
    return response


@app.get("/user/info", response_model=UserInfoResponseModel, description="获取user信息")
async def get_user_info(auth: str = Cookie(...)):
    try:
        token_info = User.decode_token(auth)
        user = await db.get_user_by_user_id(token_info.userId)
        if not user:
            raise UserServerException("userId: {} not found".format(user), error_code=404)
        return JSONResponse(content={
            "message": "ok",
            "user": dict(user)
        })
    except Exception as e:
        return JSONResponse(content={
            "message": e.message if isinstance(e, UserServerException) else repr(e),
            "user": None
        }, status_code=e.error_code if isinstance(e, UserServerException) else 500)


@app.post("/user/update", response_model=UserUpdateResponseModel, description="更新用户信息")
async def update_user_info(
        user_info: UserUpdateRequestModel,
        auth: str = Cookie(...)
):
    try:
        token_info = User.decode_token(auth)
        user = await db.get_user_by_user_id(token_info.userId)
        if not user:
            raise UserServerException("userId: {} not found".format(user), error_code=404)
        await db.upsert_user(User(**{
            **dict(user),
            **user_info.user.dict()
        }))
        return JSONResponse(content={
            "message": "success"
        })
    except Exception as e:
        return JSONResponse(content={
            "message": e.message if isinstance(e, UserServerException) else repr(e)
        }, status_code=e.error_code if isinstance(e, UserServerException) else 500)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
