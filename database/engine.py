import os

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.models import Base

load_dotenv()

# engine = create_async_engine(os.getenv("DB_LITE"), echo=True)
#
# session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
#
# async def create_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
# async def drop_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

class Database:
    def __init__(self):
        self.db_url = os.getenv("DB_LITE")
        if not self.db_url:
            raise ValueError("DB_LITE not found in .env")

        self.engine = create_async_engine(self.db_url, echo=True)
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def create_db(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except SQLAlchemyError as e:
            print(f"Error creating DB: {e}")
            raise

    async def drop_db(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except SQLAlchemyError as e:
            print(f"Error dropping DB: {e}")
            raise

    async def get_session(self) -> AsyncSession:
        async with self.session_maker() as session:
            yield session


db = Database()


# Simple model
# class Database:
#     def __init__(self):
#         self.db_url = os.getenv("DB_LITE")
#         if not self.db_url:
#             raise ValueError("DB_LITE not found in .env")
#
#         self.engine = create_async_engine(self.db_url, echo=True)
#         self.session_maker = async_sessionmaker(
#             bind=self.engine,
#             expire_on_commit=False,
#             class_=AsyncSession
#         )
#
#     async def create_db(self):
#         async with self.engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#
#     async def drop_db(self):
#         async with self.engine.begin() as conn:
#             await conn.run_sync(Base.metadata.drop_all)