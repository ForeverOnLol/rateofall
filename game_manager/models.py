from enum import Enum

from sqlalchemy import String, ForeignKey, select
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.core import Base, async_session_maker


class GameTitles(Enum):
    rate_off_all = 'roa'
    debate = 'debate'


class Game(Base):
    __tablename__ = 'game'
    game_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    game_name: Mapped[GameTitles] = mapped_column(String())
    game_data: Mapped[str] = mapped_column(String())

    lobby_id: Mapped[int] = mapped_column(ForeignKey('lobby.chat_id'), unique=True)
    lobby = relationship('Lobby', back_populates='game')

    @classmethod
    async def get_game_name_by_lobby_id(cls, lobby_id: int, async_session=async_session_maker) -> str | None:
        async with async_session() as session:
            async with session.begin():
                game = (await session.execute(select(Game).where(Game.lobby_id==lobby_id))).scalar_one_or_none()
                if game is None:
                    return None
                return game.game_name
