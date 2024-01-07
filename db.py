from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker, DeclarativeBase

import config


class Base(DeclarativeBase):
    pass


engine_configs = {"future": True, "pool_pre_ping": True}

async_session = sessionmaker(class_=AsyncSession, expire_on_commit=False)
engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, **engine_configs)
async_session.configure(
    binds={
        Base: engine,
    }
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
