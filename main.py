import asyncio
from db.services import create_tables
from telegram.tg import run_bot

if __name__ == '__main__':
    asyncio.run(create_tables())
    asyncio.run(run_bot())