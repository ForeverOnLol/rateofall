
import roa_game.models
import game_manager.models
import common.models
import lobby.models
import debate_game.models

from .core import Base, engine
async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
