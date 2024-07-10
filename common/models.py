from __future__ import annotations

from sqlalchemy import String, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column, selectinload

from common.errors import UserAlreadyInLobby
from db.core import Base


class User(Base):
    __tablename__ = 'user'
    tg_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String())
    username: Mapped[str] = mapped_column(String(), nullable=True)

    lobby_id: Mapped[int] = mapped_column(ForeignKey('lobby.chat_id'))
    lobby = relationship('Lobby', back_populates='users')

    words = relationship('HiddenWord', back_populates='user', uselist=True)

    @classmethod
    async def get(cls, tg_id: int, session: AsyncSession) -> User | None:
        '''
        Получить юзера с его лобби
        :param tg_id:
        :param session:
        :return:
        '''
        user = (await session.execute(
            select(cls).options(selectinload(cls.lobby)).where(cls.tg_id == tg_id)
        )).scalar_one_or_none()
        return user

    @classmethod
    async def create(cls, session: AsyncSession, tg_id: int, name: str, username: str, lobby_id: int) -> User:
        '''
        Создать юзера, у которого нет лобби
        :param session:
        :param tg_id:
        :param name:
        :param username:
        :return:
        '''
        user = await User.get(tg_id=tg_id, session=session)
        if user:
            raise UserAlreadyInLobby()
        if not user:
            user = User(tg_id=tg_id, name=name, username=username, lobby_id=lobby_id)
            session.add(user)
        return user


class Command:
    pass


