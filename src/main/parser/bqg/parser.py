import re
import base64
import aiohttp
from pyquery import PyQuery
from typing import Optional, Union
from src.main.util.logger import logger
from src.main.parser.exception import ParseException
from src.main.parser.model import Novel, NovelChapter
from src.main.parser.base.base_parser import BaseParser


class Parser(BaseParser):
    def __init__(self, text: str):
        self.selector = PyQuery(text)
        self.AUTHOR_RE_COMPILED = re.compile(r"作.*?者[:：](.*)")
        super().__init__(text)

    @staticmethod
    async def get_img(img_url: str):
        img_mime_type = "image/jpeg"
        prefix = "data:{};base64,"
        async with aiohttp.ClientSession() as session:
            res = await session.get(img_url, ssl=False)
            if res.status == 200 and res.headers.get("Content-Type"):
                img_mime_type = res.headers["Content-Type"]
            image_data = base64.b64encode(await res.read()).decode()
        return prefix.format(img_mime_type) + image_data

    async def parse_cover(self) -> Optional[str]:
        try:
            img_url = self.selector("meta[property='og:image']").attr("content")
            if not img_url:
                img_url = self.selector("#fmimg>img").attr("src")
            if not img_url:
                return
            return await self.get_img(img_url)
        except Exception as e:
            logger.exception(e)

    def parse_novel(self) -> Novel:
        lines = self.selector("#maininfo").text().split("\n")
        result = {
            "name": None,
            "briefIntroduction": None
        }
        for line in lines:
            if result["name"] is None:
                result["name"] = line
            else:
                regex_author = self.AUTHOR_RE_COMPILED.search(line)
                if regex_author:
                    result["author"] = regex_author.group(1)
                else:
                    result["briefIntroduction"] = line
        return Novel(**result)

    def clean_novel_chapter_content_lines(self):
        self.selector.remove("#content p")

    def parse_novel_chapter(self) -> NovelChapter:
        self.clean_novel_chapter_content_lines()
        lines = self.selector("#content").text().split("\n")
        name = self.selector(".bookname>h1").text()
        if not name or not lines:
            raise ParseException("not a valid novel chapter, can not find {}".format(
                "name and line" if not name and not lines else "name" if not name else "line"
            ))
        content = "\n".join(list(filter(lambda x: x, lines)))
        return NovelChapter(name=name, content=content)

    def parse(self) -> Union[Novel, NovelChapter]:
        if self.selector("#maininfo"):
            return self.parse_novel()
        elif self.selector("#content"):
            return self.parse_novel_chapter()
        raise ParseException("not a bqg novel or novel chapter")


if __name__ == '__main__':
    import asyncio
    # with open("../data/novel_detail_page.html") as f:
    #     data = f.read()
    # parser = Parser(data)
    # print(parser.parse_novel())
    # print(asyncio.run(parser.parse_cover()))
    with open("../data/novel_chapter_detail_page_3.html") as f:
        data = f.read()
    s = PyQuery(data)
    s.remove("#content p")
    print(s("#content").text().split("\n"))
    parser = Parser(data)
    print(parser.parse_novel_chapter())
