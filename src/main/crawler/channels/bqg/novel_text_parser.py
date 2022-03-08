from typing import List
from pyquery import PyQuery


class Application:
    @staticmethod
    def parse_novel_list_page(selector: PyQuery) -> List[str]:
        novel_list = selector("#newscontent>.l>ul>li")
        result = [
            novel(".s3>a").attr("href")
            for novel in novel_list.items()
        ]
        return list(filter(lambda x: x.strip(), result))

    @staticmethod
    def parse_novel_chapter_list(selector: PyQuery) -> List[str]:
        novel_chapter_list = selector("#list>dl>dd")
        result = [
            novel_chapter("a").attr("href")
            for novel_chapter in novel_chapter_list.items()
        ]
        return list(filter(lambda x: x.strip(), result))

    def parse(self, text: str):
        selector = PyQuery(text)
        if selector("#newscontent>.l>ul"):
            return self.parse_novel_list_page(selector)
        elif selector("#list"):
            return self.parse_novel_chapter_list(selector)
        return
