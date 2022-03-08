import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class RsaCipher:
    def __init__(self, private_key: str):
        self.private_key = RSA.import_key(private_key.encode())
        self.cipher = PKCS1_v1_5.new(self.private_key)

    def decrypt(self, text) -> str:
        _text = base64.b64decode(text)
        return self.cipher.decrypt(_text, None).decode()


if __name__ == '__main__':
    p_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCSYyi72IFMQMYmregKTaaeNsyBAtj7hA+BembvFFlRvQpk2853
D1uRzewpF26H9c28ZVT27MivwYJMBEJaICUJfLWDSItwDWxlcTl9lATk3HLL+ZhL
ZNZRJFT+RQSPkP5mcNUgutBrZOTIKSHCjDvE2MkVPajLLaXE13pRhdQCAwIDAQAB
AoGAAmLEhALE2aVrq+uYB0L15nX8h/pzyP0nEiGCGdlNDbjPXyU1fYbMFI5DrkC1
Ru9n7xxaCGJWndEMgj2ZaZi9Ojzd2P0Zgps2hApR8BbUgBfIC7IUdhcs59rR7LDS
2crQNHO8Sm1jl/pgAZcjSyUbWySAA2qqqelxX7lUfTIw+aECQQC74jDvZpkzAOHw
PaYTnJHQgM9STSS37H5oNMTNfusrw8drh5n6SAjQNQb29UrT6AzFm57apXq0r1sy
iQrKcIObAkEAx3WhNq4zXPweDF3QCvBSlZkCi3QqOxGzVTQbmJ9SrTdp4j7Ev9Kj
ab8S6yGSfuko0AR0s3710m7090EziTaluQJAY8te5qn+UYL0f2CfZ+dP5AmnFTX4
fODWu47bwbLaQuK4d7sM5E2CsOSZkG71kdy9e/COzd/7byF9NThpTOG6ZQJBAJV9
Jcxzlu9Tzbl6/heUsnCIcw3NjHEk/QEYwq4Kis5jv6nfXVpfJjZ1DFrJmKAhY4M0
M7rrppWGr3Y4mcV2/ZECQDFhAeRtL75erW+xkhwuitClmGT4AgdONB7frpdKzUoK
bqumfT6wPsv2qq9cSdS53JkaF1UCp21JJ0OejEot/qQ=
-----END RSA PRIVATE KEY-----"""
    r = RsaCipher(p_key)
    print(r.decrypt("dnw6EJQ5K9wAC6EpMmYH7bJPZ6Er7LPnE90Kn+E9vcSJw2ACOW5Qjeu9wAnl115e1r70h7+lla2p3Ksr9HfTpMXHzTplcc"
                    "oFzhV62XoiwnH3CuWHow/DgLOK+OfhFp+JHgunyIbbNzXELZcSExdUj7v7g5z263may8xXezXW5FU="))
