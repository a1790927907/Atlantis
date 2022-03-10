import os

pg_user = os.getenv('POSTGRES_USER', 'postgres')
pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
pg_host = os.getenv('POSTGRES_HOST', 'localhost')
pg_port = int(os.getenv('POSTGRES_PORT', '5433'))
pg_database = os.getenv('POSTGRES_DB', 'novel')

DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"

novel_type = [
    {"code": 1, "cn": "玄幻"},
    {"code": 2, "cn": "修真"},
    {"code": 3, "cn": "都市"},
    {"code": 4, "cn": "穿越"},
    {"code": 5, "cn": "网游"},
    {"code": 6, "cn": "科幻"}
]
