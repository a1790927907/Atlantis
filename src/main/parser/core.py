from typing import Type, Optional
from src.main.parser.config import Settings
from src.main.parser.model import Novel, NovelChapter
from src.main.parser.exception import ParseServerException
from src.main.parser.bqg.parser import Parser as BQGParser


class Application:
    def __init__(self, settings: Type[Settings]):
        self.settings = settings

    def get_meta(self, url: Optional[str] = None):
        return {
            "version": self.settings.version,
            "author": self.settings.author,
            "maintainer": self.settings.maintainer,
            "detectedSource": url
        }

    @staticmethod
    def choose_parser(url: str, text: str):
        if "xbiquge.la" in url:
            return BQGParser(text)
        raise ParseServerException("can not find parser, url: {}".format(url), error_code=404)

    async def parse(self, url: str, text: str, parse_cover: bool):
        parser = self.choose_parser(url, text)
        result = parser.parse()
        if isinstance(result, Novel):
            result_type = "Novel"
            if parse_cover:
                result.cover = await parser.parse_cover()
        elif isinstance(result, NovelChapter):
            result_type = "NovelChapter"
        else:
            raise ParseServerException("unknown parse result type", error_code=400)
        return {
            "meta": self.get_meta(url),
            "result": result,
            "sourceType": result_type
        }
