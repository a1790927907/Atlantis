import os
import aiohttp
import asyncio
from loguru import logger
from typing_extensions import Literal
from typing import List, Dict, Type, Optional, Union, cast
from src.main.crawler.channels.bqg.model import NovelTypeMapper
from src.main.crawler.channels.bqg.exception import NovelBQGCrawlerException
from src.main.crawler.channels.bqg.novel_text_parser import Application as ParserApp


class Application:
    def __init__(
            self, novel_type_mapper: NovelTypeMapper, client_session: Type[aiohttp.ClientSession],
            parser: ParserApp,
            novel_type: Optional[List[Literal[
                'xuanhuanxiaoshuo', 'xiuzhenxiaoshuo', 'dushixiaoshuo',
                'chuanyuexiaoshuo', 'wangyouxiaoshuo', 'kehuanxiaoshuo'
            ]]] = None
    ):
        if novel_type is None:
            novel_type = [
                'xuanhuanxiaoshuo', 'xiuzhenxiaoshuo', 'dushixiaoshuo',
                'chuanyuexiaoshuo', 'wangyouxiaoshuo', 'kehuanxiaoshuo'
            ]
        self.channel = "xbiquge"
        self.channel_cn = "笔趣阁"
        self.host = os.getenv("HOST", "https://www.xbiquge.la")
        self.base_home_page_url = os.getenv("BASE_HOME_PAGE_URL", "https://www.xbiquge.la/")
        self.novel_type_mapper = novel_type_mapper.detail
        self.client_session = client_session
        self.parser = parser
        self.start_urls: List[Dict[Literal['url', 'cn', 'code'], Union[int, str]]] = cast(
            List[Dict[Literal['url', 'cn', 'code'], Union[int, str]]],
            [
                {
                    "url": self.base_home_page_url + _type + "/",
                    "code": self.novel_type_mapper[_type].code,
                    "cn": self.novel_type_mapper[_type].cn
                }
                for _type in novel_type if _type in self.novel_type_mapper
            ]
        )
        self.max_novel_type_fetcher = int(os.getenv("MAX_NOVEL_TYPE_FETCHER", "1"))
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/92.0.4515.107 Safari/537.36"
        }

    async def fetch_page(self, url: str, headers=None):
        headers = self.base_headers if headers is None else headers
        async with self.client_session() as session:
            res = await session.get(url, ssl=False, headers=headers)
            if res.status == 200:
                result = await res.text()
            else:
                raise NovelBQGCrawlerException("request url: {} error, status code: {}".format(
                    res.url.human_repr(), res.status
                ))
        return result

    def get_novel_chapter_page_url(self, novel_detail: str, url: Optional[str] = None) -> List[str]:
        novel_chapter_url = self.parser.parse(novel_detail)
        if novel_chapter_url is None:
            raise NovelBQGCrawlerException("url: {} parse novel detail error, text: {}".format(
                url, novel_detail
            ))
        return [
            self.host + url
            for url in novel_chapter_url
        ]

    async def fetch_novel_list(self, url: str) -> List[str]:
        text = await self.fetch_page(url)
        novel_list_url = self.parser.parse(text)
        if novel_list_url is None:
            raise NovelBQGCrawlerException("url: {} parse novel list error, text: {}".format(
                url, text
            ))
        novel_list_url = [
            self.host + url
            for url in novel_list_url
        ]
        return novel_list_url

    async def _fetch(self, url: str, code: int):
        novel_list_url = await self.fetch_novel_list(url)
        for novel_url in novel_list_url:
            novel_detail = await self.fetch_page(novel_url)
            # 这里留着parse novel
            # parse完需要存储下来

            novel_chapter_url_list = self.get_novel_chapter_page_url(novel_detail, url=novel_url)
            for novel_chapter_url in novel_chapter_url_list:
                novel_chapter_detail = await self.fetch_page(novel_chapter_url)
                # 这里留着 parse novel chapter

    async def fetch(self, url: str, code: int):
        try:
            await self._fetch(url, code)
        except NovelBQGCrawlerException as e:
            logger.error(e.message)
        except Exception as e:
            logger.exception(e)

    async def _start_synchronize(self):
        def cut_params(source: List[List[str]]) -> List[List[List[str]]]:
            result, temp_result = [], []
            for _source in source:
                if len(temp_result) >= self.max_novel_type_fetcher:
                    result.append(temp_result)
                    temp_result = []
                else:
                    temp_result.append(_source)
            if temp_result:
                result.append(temp_result)
            return result
        params_list = []
        for start_config in self.start_urls:
            code = start_config[cast(Literal['url', 'cn', 'code'], "code")]
            url = start_config[cast(Literal['url', 'cn', 'code'], "url")]
            params_list.append([url, code])
        params_cut_list = cut_params(params_list)
        for params in params_cut_list:
            await asyncio.gather([
                self.fetch(*_params)
                for _params in params
            ])
