import os

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from common.texts_for_db import description_for_info_pages, categories
from database.models import Base
from database.orm_query import orm_create_categories, orm_add_banner_description

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


# Postgresql
class Database:
    def __init__(self):
        self.db_url = os.getenv("DB_URL")
        if not self.db_url:
            raise ValueError("DB_URL not found in .env")

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

            async with self.session_maker() as session:
                await orm_create_categories(session, categories)
                await orm_add_banner_description(session, description_for_info_pages)
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

    async def close(self):
        try:
            if self.engine:
                await self.engine.dispose()
                print("Database engine disposed")
        except Exception as e:
            print(f"Error closing database: {e}")


# # SQLite
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
#         try:
#             async with self.engine.begin() as conn:
#                 await conn.run_sync(Base.metadata.create_all)
#         except SQLAlchemyError as e:
#             print(f"Error creating DB: {e}")
#             raise
#
#     async def drop_db(self):
#         try:
#             async with self.engine.begin() as conn:
#                 await conn.run_sync(Base.metadata.drop_all)
#         except SQLAlchemyError as e:
#             print(f"Error dropping DB: {e}")
#             raise
#
#     async def get_session(self) -> AsyncSession:
#         async with self.session_maker() as session:
#             yield session
#
#     async def close(self):
#         try:
#             if self.engine:
#                 await self.engine.dispose()
#                 print("Database engine disposed")
#         except Exception as e:
#             print(f"Error closing database: {e}")

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