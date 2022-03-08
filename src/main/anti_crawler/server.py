import aiofiles

from fastapi import FastAPI, Header
from src.main.util.logger import logger
from fastapi.staticfiles import StaticFiles
from src.main.anti_crawler.core import CoreValidator
from src.main.anti_crawler.client import RedisClient
from src.main.anti_crawler.rsa_cipher import RsaCipher
from src.main.anti_crawler.aes_cipher import AesCipher
from fastapi.responses import JSONResponse, HTMLResponse
from src.main.anti_crawler.config import AES_MODE, AES_KEY, RSA_PRIVATE_KEY, JWT_KEY, ALG, REDIS_SERVER, REDIS_PORT


app = FastAPI(docs_url="/anti-crawler/docs", redoc_url="/anti-crawler/re_docs", description="验证加密参数")
app.mount("/anti-crawler/static", StaticFiles(directory="./static"), name="static")
aes_cipher = AesCipher(AES_MODE, AES_KEY)
rsa_cipher = RsaCipher(RSA_PRIVATE_KEY)
client = RedisClient(redis_url=REDIS_SERVER, port=REDIS_PORT)


@app.post("/anti-crawler/validate", description="validate")
async def validate(
        body: dict,
        n: str = Header(..., description="次数"),
        en: str = Header(..., description="密文")
):
    try:
        decrypted_n = rsa_cipher.decrypt(n)
        enc_num = int(decrypted_n.split("+")[0])
        redis_client = await client.connect()
        core_validator = CoreValidator(enc_num, en, JWT_KEY, body, aes_cipher, redis_client, ALG)
        await core_validator.validate()
        return JSONResponse(content={
            "message": "ok"
        }, status_code=200)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(content={
            "message": "validate error"
        }, status_code=500)


@app.get("/anti-crawler/frame", description="iframe用", response_class=HTMLResponse)
async def index():
    async with aiofiles.open("./template/index.html") as f:
        data = await f.read()
    return data


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
