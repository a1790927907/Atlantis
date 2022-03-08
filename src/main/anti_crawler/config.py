import os

from Crypto.Cipher import AES


AES_MODE = int(os.getenv("AES_MODE", AES.MODE_ECB))
AES_KEY = os.getenv("AES_KEY", "zyh000011112222z")

RSA_PRIVATE_KEY = os.getenv("RSA_PRIVATE_KEY", """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----""")

JWT_KEY = os.getenv("JWT_KEY", "zyh123456789")
ALG = os.getenv("ALG", "HS256")

REDIS_SERVER = os.getenv("REDIS_SERVER", "redis://localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
