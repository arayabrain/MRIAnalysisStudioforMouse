from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_timestamp
from sqlmodel import SQLModel

from backend.core.config import settings

from .ultils import camel_to_snake

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_recycle=360,
    pool_size=20,
    pool_pre_ping=False,
    echo=settings.ECHO_SQL,
)
# testing_engine = create_async_engine(
#     settings.DATABASE_TESTING_URL, pool_recycle=360, pool_size=20, pool_pre_ping=False, echo=settings.ECHO_SQL
# )

async_session = sessionmaker(
    engine,
    autoflush=False,
    future=True,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_session() -> AsyncSession:
    """
    TODO: missing function docstring
    """
    return async_session()


async def get_db() -> AsyncSession:
    """
    TODO: missing function docstring
    """
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as err:
            print(err)

async def init_db():
    """
    TODO: missing function docstring
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@as_declarative()
class Base:
    id = Column(BigInteger, primary_key=True, index=True)
    __name__: str

    @declared_attr
    def __table_args__(self):
        return {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
        }

    @declared_attr
    def __tablename__(self) -> str:
        return camel_to_snake(self.__name__, is_plural=True)


class TimestampMixin:
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=current_timestamp(),
        index=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=current_timestamp(),
        onupdate=current_timestamp(),
    )
