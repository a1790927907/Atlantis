import os


pg_user = os.getenv('POSTGRES_USER', 'postgres')
pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
pg_host = os.getenv('POSTGRES_HOST', 'localhost')
pg_port = int(os.getenv('POSTGRES_PORT', '5433'))
pg_database = os.getenv('POSTGRES_DB', 'user')

# 单位: 天
DEFAULT_TOKEN_EXPIRE_TIME = int(os.getenv("DEFAULT_TOKEN_EXPIRE_TIME", "7"))
DEFAULT_JWT_SECRET = os.getenv("DEFAULT_JWT_SECRET", "zyh123456")
DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
