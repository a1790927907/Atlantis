import base64
from typing import Optional
from Crypto.Cipher import AES


class AesCipher:
    def __init__(self, mode: int, key: str, iv: Optional[bytes] = None):
        if iv:
            self.crypto = AES.new(key.encode(), mode, iv)
        else:
            self.crypto = AES.new(key.encode(), mode)

    def decrypt(self, target: str) -> str:
        text_b = base64.b64decode(target)
        base64_text = self.crypto.decrypt(text_b).decode()
        return base64_text[0:-ord(base64_text[-1])]

    @staticmethod
    def add_to_16(target: str):
        pad = 16 - len(target.encode('utf-8')) % 16
        text = target + pad * chr(pad)
        return text.encode('utf-8')

    def encrypt(self, target: str) -> str:
        text = self.add_to_16(target)
        cipher_text = self.crypto.encrypt(text)
        return base64.b64encode(cipher_text).decode()


if __name__ == '__main__':
    import json

    _key = "zyh000011112222z"
    c = AesCipher(AES.MODE_ECB, _key)
    print(c.encrypt("1111"))
    _ = json.dumps({"account": "123", "password": "123"}, separators=(",", ":"))
    print(_)
    print(c.encrypt(_))
    print(c.decrypt("ZoTKr+Pkbjy8Im0WjU2eoHit1mK/y9WIOmI3I26cW8cuzhWKu+9gQIpoAp5l5L0V"))
