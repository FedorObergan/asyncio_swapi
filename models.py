import os

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ваш пароль")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ваш user")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ваше название db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5430")

PG_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_async_engine(PG_DSN)
SessionDB = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):

    __tablename__ = "swapi_people"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    birth_year: Mapped[str] = mapped_column(String(64))
    eye_color: Mapped[str] = mapped_column(String(64))
    films: Mapped[str] = mapped_column(String(200), nullable=True)
    gender: Mapped[str] = mapped_column(String(64))
    hair_color: Mapped[str] = mapped_column(String(64))
    height: Mapped[str] = mapped_column(String(64))
    homeworld: Mapped[str] = mapped_column(String(64))
    mass: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(64))
    skin_color: Mapped[str] = mapped_column(String(64))
    species: Mapped[str] = mapped_column(String(200), nullable=True)
    starships: Mapped[str] = mapped_column(String(200), nullable=True)
    vehicles: Mapped[str] = mapped_column(String(200), nullable=True)


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
