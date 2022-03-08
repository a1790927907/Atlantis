import uuid
import aiohttp
from src.main.user.database_model import Base, engine
from src.main.user.exception import UserServerException
from src.main.user.config import ANTI_CRAWLER_VALIDATE_URL


def get_uuid() -> str:
    return uuid.uuid4().__str__()


async def check_request_validation(body: dict, headers: dict):
    async with aiohttp.ClientSession() as session:
        res = await session.post(ANTI_CRAWLER_VALIDATE_URL, json=body, headers={
            "n": headers.get("n") or "",
            "en": headers.get("en") or ""
        })
    if res.status != 200:
        raise UserServerException((await res.json())["message"], error_code=res.status)


def create_tables():
    Base.metadata.create_all(bind=engine)
