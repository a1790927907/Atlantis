from typing import Optional
from fastapi.responses import Response
from src.main.parser.config import Settings
from src.main.parser.core import Application
from src.main.parser.model import ParseResponse
from fastapi import FastAPI, UploadFile, Query, File
from src.main.parser.exception import ParseException, ParseServerException


app = FastAPI(docs_url="/parse/docs", redoc_url="/parse/re_doc")
parser_app = Application(Settings)


@app.post("/api/parse", response_model=ParseResponse, description="解析 v1")
async def parse(
        response: Response,
        novel: Optional[UploadFile] = File(..., description="数据文本"),
        url: str = Query(default=..., description="来源"),
        parse_cover: bool = Query(default=False, title="是否尝试解析封面")
):
    try:
        text = await novel.read()
        result = await parser_app.parse(url, text.decode(), parse_cover)
        return {
            "message": "ok",
            **result
        }
    except Exception as e:
        response.status_code = 500
        if isinstance(e, ParseServerException):
            response.status_code = e.error_code
            message = e.message
        elif isinstance(e, ParseException):
            message = e.message
        else:
            message = repr(e)
        return {
            "meta": parser_app.get_meta(parse_request.url),
            "message": message
        }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9500)
