import pymysql
from sqlalchemy import (Column, Integer, String,
                        create_engine)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import create_database, database_exists

from rabbitmq.models.config import Settings, get_settings

settings: Settings = get_settings()

Base = declarative_base()

class PayloadMsg(Base):
    __tablename__ = "payload_messages"

    message_id = Column(Integer, autoincrement=True, primary_key=True)
    client_id = Column(String(20), nullable=False)
    event_type = Column(String(20), nullable=False)
    message_body = Column(String(500))
    remark = Column(String(100))

def init_db(dsn: str):
    try:
        engine = create_engine(
            dsn,
            pool_pre_ping=True,
            pool_recycle=settings.db_pool_recycle,
            connect_args={
                "read_timeout": settings.db_read_timeout,
                "write_timeout": settings.db_write_timeout
            }
        )
        if not database_exists(engine.url):
            create_database(engine.url)

        Base.metadata.create_all(engine)
        return engine
    except OperationalError as e:
        print(f"Error: {e}")
        pass
    except pymysql.err.OperationalError as e:
        print(f"Error: {e}")
        pass
