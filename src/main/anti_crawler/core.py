import os
import jwt
import json
import pytz
import aioredis

from typing import Union
from hashlib import md5, sha256
from src.main.util.time_utils import get_now
from src.main.anti_crawler.aes_cipher import AesCipher


class CoreValidator:
    def __init__(
            self, n: int, raw_string: str, jwt_key: str, body: Union[str, dict], aes_cipher: AesCipher,
            redis_client: aioredis.Redis, jwt_alg: str = "HS256"
    ):
        self.n = n
        self.raw_string = raw_string
        self.jwt_key = jwt_key
        self.jwt_alg = jwt_alg
        self.aes_cipher = aes_cipher
        self.body = body
        self.redis_client = redis_client
        self.redis_key = "anti_crawler_enc"
        self.max_time_difference_deviation = int(os.getenv("TIME_DEVIATION", "0"))

    def decode_jwt(self, raw: str) -> dict:
        return jwt.decode(raw, key=self.jwt_key, algorithms=[self.jwt_alg])

    def encrypt(self, raw: str) -> str:
        result = raw
        for i in range(self.n):
            if i % 2 == 0:
                result = md5(result.encode()).hexdigest()
            else:
                result = sha256(result.encode()).hexdigest()
        replaced_val = ['0', '1', '2', 'a', 'b', 'z', 'y', 'h']
        for val in replaced_val:
            result = result.replace(val, "")
        return result

    async def check_raw_string_validation(self):
        if await self.redis_client.sismember(self.redis_key, self.raw_string):
            raise Exception("麻瓜")
        await self.redis_client.sadd(self.redis_key, self.raw_string)

    async def check_time_difference(self, jwt_decoded_value: dict):
        now = get_now(return_type="timestamp", timezone=pytz.timezone("Asia/Shanghai"))
        if jwt_decoded_value["end"] < now * 1000 + self.max_time_difference_deviation:
            raise Exception("expire")

    async def validate(self):
        await self.check_raw_string_validation()
        jwt_decoded_value = self.decode_jwt(self.raw_string)
        assert "body" in jwt_decoded_value
        await self.check_time_difference(jwt_decoded_value)
        enc_checked = self.aes_cipher.decrypt(jwt_decoded_value["body"])
        enc = self.encrypt(json.dumps(
            self.body, separators=(",", ":")
        ) if isinstance(self.body, dict) else self.body)
        if enc_checked == enc:
            return
        raise Exception("validate error, enc: {}, enc checked: {}".format(enc, enc_checked))


if __name__ == '__main__':
    from src.main.anti_crawler.aes_cipher import AesCipher
    from src.main.anti_crawler.config import AES_MODE, AES_KEY
    _aes_cipher = AesCipher(AES_MODE, AES_KEY)
    r = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdGFydCI6MTY0NDc2Mjc5ODUzOCwiZW5kIjoxNjQ0NzYyNzk4NTU4LCJib" \
        "2R5IjoiYnlUdVN5SS9sQ3kyZ0JzZUdublBFWnFqdHlxTFFqdnJuclc0M2NBTHBabGtIc2NBSWpjWGthNlBxWkNFdDhURSJ9.28X26" \
        "mTg9N4wNbvwTbH6wyyQWsZ2uyEcl-6JjgMiyKc"
    k = "zyh123456789"
    core_cipher = CoreValidator(10, r, k, {"account": "123", "password": "123"}, _aes_cipher)
    core_cipher.validate()
