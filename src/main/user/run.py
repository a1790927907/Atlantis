from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.main.util.time_utils import get_now
from src.main.user.config import DATABASE_URL
from src.main.user.database_class import DataBase
from src.main.user.exception import UserServerException
from src.main.user.model import UserRegisterResponseModel, UserRegisterRequestModel, User


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


@app.post("/user/login", description="登录")
async def login():
    return
