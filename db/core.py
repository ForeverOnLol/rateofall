from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Создание файла базы данных SQLite
engine = create_async_engine('sqlite+aiosqlite:///database.db')
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
