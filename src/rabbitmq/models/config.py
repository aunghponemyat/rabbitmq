from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_filename: str = "log"

    rbq_queue_name: str = "test"
    rbq_username: str = "user"
    rbq_password: str = "password"
    rbq_host: str = "localhost"
    rbq_port: str = "5672"
    rbq_vhost: str = "vhost"

    db_dsn: str = "mysql+pymysql://root@127.0.0.1:4000/ltsdb"
    db_read_timeout: int = 60
    db_write_timeout: int = 60
    db_pool_recycle: int = 3600

@lru_cache
def get_settings() -> Settings:
    settings = Settings(_env_file=".env")
    return settings
