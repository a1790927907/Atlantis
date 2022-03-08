class BaseParser:
    def __init__(self, text: str):
        self.text = text

    def parse_cover(self):
        return

    def parse_novel(self):
        raise NotImplementedError

    def parse(self):
        raise NotImplementedError
