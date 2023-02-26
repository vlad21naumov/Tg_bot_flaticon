from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import BigInteger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
PG_URL = os.getenv('PG_URL')
Base = declarative_base()
engine = create_async_engine(
    PG_URL
    # echo=True,
)


class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, primary_key=True, index=True)
    user_login = Column(String(255))
    user_name = Column(String(100))


class Icons(Base):
    __tablename__ = "icons"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.user_id"))
    icon_url = Column(String(100))
    category = Column(String(250))

