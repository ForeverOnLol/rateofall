from __future__ import annotations

import asyncio
import datetime
from datetime import timedelta
from enum import Enum
from typing import Callable

from sqlalchemy import String, select, DATETIME, ForeignKey, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column, selectinload

import config
from common.helpers import wait_timeout
from common.models import User
from db.core import Base, async_session_maker
from lobby import middlewares
from lobby.errors import FillerAlreadyUsed, MaxWordCount, EmptyParty, GameIsRunning, EmptyWords, CantStopWhileFiller
from roa_game.errors import GameIsNotExist


class LobbyStates(Enum):
    wait_members = 'wait_members'
    word_filling = 'word_filling'
    game_running = 'game_running'

    def __str__(self):
        return self.value


class Lobby(Base):
    __tablename__ = 'lobby'
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[str] = mapped_column(String(), default=LobbyStates.word_filling.value)

    users = relationship('User', back_populates='lobby', cascade="all, delete-orphan")
    countdown_timer = relationship('CountdownTimer', uselist=True, back_populates="lobby", cascade="all, delete-orphan")
    words = relationship('HiddenWord', back_populates='lobby', uselist=True, cascade="all, delete-orphan")
    game = relationship('Game', back_populates='lobby', cascade="all, delete-orphan")

    def __repr__(self):
        return f'CHAT_ID: {self.chat_id}\nUsers: {self.users}'

    @classmethod
    async def get(cls, session: AsyncSession, chat_id: int) -> Lobby | None:
        '''
        Получить лобби с его пользователями
        :param session:
        :param chat_id:
        :return:
        '''
        lobby = (await session.execute(
            select(cls).options(selectinload(cls.users)).where(Lobby.chat_id == chat_id)
        )).scalar_one_or_none()
        return lobby

    @classmethod
    async def is_exist(cls, session: AsyncSession, chat_id: int) -> bool:
        '''
        Проверка, что лобби существует.
        :param session:
        :param chat_id:
        :return:
        '''
        if await cls.get(session=session, chat_id=chat_id):
            return True
        return False

    @classmethod
    async def create(cls, session: AsyncSession, chat_id: int, state: str = LobbyStates.wait_members.value,
                     users: list = []) -> Lobby:
        '''
        Создать лобби
        :param session:
        :param chat_id:
        :param state:
        :param users:
        :return:
        '''
        lobby = await Lobby.get(chat_id=chat_id, session=session)
        if not lobby:
            lobby = Lobby(chat_id=chat_id, state=state, users=users)
            session.add(lobby)
        return lobby

    @classmethod
    async def destroy(cls, chat_id: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                lobby = await cls.get(session=session, chat_id=chat_id)
                if lobby:
                    if await lobby.is_fill_words_state():
                        raise CantStopWhileFiller()
                    await session.delete(lobby)
        return None

    @classmethod
    async def add_member(cls, user_id: int, chat_id: int, username: str, name: str,
                         async_session=async_session_maker):
        '''
        Добавить участника в конкретное лобби.
        Если лобби не существует - оно создаётся.
        :param user_id:
        :param chat_id:
        :param username:
        :param name:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                await Lobby.create(chat_id=chat_id, session=session)
                await User.create(tg_id=user_id, name=name, username=username, session=session, lobby_id=chat_id)
                await session.commit()
        return None

    @classmethod
    async def get_members(cls, chat_id: int, async_session=async_session_maker) -> list[User.name]:
        '''
        Получить список участников определенного лобби.
        :param chat_id:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                lobby = await cls.get(session=session, chat_id=chat_id)
                if not lobby:
                    return []
                lobby_users = [user.name for user in lobby.users]
                return lobby_users

    async def get_members_id_name_tuple(self) -> list[tuple[User.tg_id, User.name]]:
        return [(user.tg_id, user.name) for user in self.users]

    async def fill_words_state(self):
        self.state = LobbyStates.word_filling.value

    async def game_running_state(self):
        self.state = LobbyStates.game_running.value

    async def is_fill_words_state(self):
        return self.state == LobbyStates.word_filling.value

    @classmethod
    async def is_ready_for_game(cls, session, chat_id: int) -> bool:
        lobby = await Lobby.get(chat_id=chat_id, session=session)
        if not lobby:
            raise EmptyParty()
        return True

    async def is_game_running_state(self):
        return self.state == LobbyStates.game_running.value


class CountdownTimer(Base):
    __tablename__ = 'countdown_timers'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_time: Mapped[datetime.datetime] = mapped_column(
        DATETIME(timezone=True), default=datetime.datetime.utcnow()
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DATETIME(timezone=True), default=datetime.datetime.utcnow() + timedelta(seconds=config.send_word_seconds)
    )

    lobby_id: Mapped[int] = mapped_column(ForeignKey('lobby.chat_id'), unique=True)
    lobby = relationship('Lobby', back_populates='countdown_timer')

    @classmethod
    async def get(cls, session: AsyncSession, lobby_id: int) -> CountdownTimer | None:
        '''
        Получить существующий таймер для лобби.
        :param lobby_id:
        :param async_session:
        :return:
        '''
        timer = (await session.execute(
            select(cls).where(CountdownTimer.lobby_id == lobby_id)
        )).scalar_one_or_none()
        return timer

    # @classmethod
    async def get_by_user_id(cls, session: AsyncSession, user_id: int) -> CountdownTimer | None:
        '''
        Получить существующий таймер для лобби.
        СДЕЛАТЬ! ТУТ ВОЗНИКАЕТ ПРОБЛЕМА С 2 И БОЛЕЕ БЕСЕДАМИ!
        :param lobby_id:
        :param async_session:
        :return:
        '''
        # timer = (await session.execute(
        #     select(cls).where(cls.lobby_id == )
        # )).scalar_one_or_none()
        # return timer

    @classmethod
    async def create(cls, session: AsyncSession, lobby_id: int) -> CountdownTimer:
        '''
        Создать таймер.
        :param lobby_id:
        :param async_session:
        :return:
        '''
        timer = await CountdownTimer.get(session=session, lobby_id=lobby_id)
        if not timer:
            timer = cls(lobby_id=lobby_id)
            session.add(timer)
        return timer

    async def is_running(self) -> bool:
        '''
        Проверка на то, что таймер запущен.
        :return:
        '''
        current_time = datetime.datetime.utcnow()
        if (self.start_time <= current_time) and (self.end_time >= current_time):
            return True
        return False

    @classmethod
    async def is_exist(cls, session: AsyncSession, lobby_id: int) -> bool:
        '''
        Проверка что таймер существует
        :param lobby_id:
        :param async_session:
        :return:
        '''
        if await cls.get(session, lobby_id):
            return True
        return False

    async def is_used(self) -> bool:
        '''
        Проверка что таймер уже был использован.
        :param lobby_id:
        :param async_session:
        :return:
        '''
        current_time = datetime.datetime.utcnow()
        if (self.end_time < current_time):
            return True
        return False

    @classmethod
    async def run(cls, lobby_id: int, session: AsyncSession) -> CountdownTimer:
        '''
        Инициализировать таймер.
        :param lobby_id:
        :param async_session:
        :return:
        '''
        timer = await CountdownTimer.create(session=session, lobby_id=lobby_id)
        return timer


class HiddenWord(Base):
    __tablename__ = 'hidden_word'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String())

    lobby_id: Mapped[int] = mapped_column(ForeignKey('lobby.chat_id'))
    lobby = relationship('Lobby', back_populates='words')

    user_id: Mapped[int] = mapped_column(ForeignKey('user.tg_id'))
    user = relationship('User', back_populates='words')

    @classmethod
    async def get(cls, session: AsyncSession, lobby_id: int, value: str) -> HiddenWord | None:
        '''
        Получить объект слова по значению и id лобби.
        :param chat_id:
        :param async_session:
        :param value:
        :return:
        '''
        word = (await session.execute(
            select(cls).where(HiddenWord.lobby_id == lobby_id, HiddenWord.value == value)
        )).scalar_one_or_none()
        return word

    @classmethod
    async def create(cls, session: AsyncSession, lobby_id: int, word: str, user_id: int) -> HiddenWord:
        '''
        Создать слово.
        :param chat_id:
        :param async_session:
        :param user_id:
        :return:
        '''
        hidden_word = HiddenWord(lobby_id=lobby_id, value=word, user_id=user_id)
        session.add(hidden_word)
        return hidden_word

    @classmethod
    async def get_list(cls, session: AsyncSession, lobby_id: int, in_str=True) -> list[HiddenWord]:
        '''
        Получить список слов по id лобби.
        :param session:
        :param lobby_id:
        :param in_str: Нужен ли вывод списка со строками. а не моделями. True по умолчанию
        :return:
        '''
        word_list = (await session.execute(
            select(cls).where(HiddenWord.lobby_id == lobby_id)
        )).scalars()
        if not word_list:
            print(word_list)
            raise EmptyWords()
        word_list = list(word_list)
        if in_str:
            word_list = [word.value for word in word_list]
        return word_list

    @classmethod
    async def count_personal_words(cls, session: AsyncSession, user_id: int):
        word_list = (await session.execute(
            select(HiddenWord)
            .join(User, User.tg_id == HiddenWord.user_id)
            .where(HiddenWord.user_id == user_id)
        )).scalars()
        return len(list(word_list))


class WordProvider():
    @classmethod
    @middlewares.lobby_not_empty
    @middlewares.wait_members_state
    async def start(cls, lobby_id: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                if await cls.is_not_active(session=session, lobby_id=lobby_id):
                    lobby = (await Lobby.get(session=session, chat_id=lobby_id))
                    if lobby:
                        await lobby.fill_words_state()
                    await CountdownTimer.run(lobby_id=lobby_id, session=session)

    @classmethod
    @middlewares.user_in_lobby
    @middlewares.fill_word_state
    async def fill_word(cls, user_id: int, word: str, async_session=async_session_maker) -> int:
        '''
        1) Проверить, что юзер есть
        2) Проверить, что состояние - заполнение
        3) Проверить, что ограничения по словам совпадает
        :param user_id:
        :param word:
        :param async_session:
        :return:
        '''
        async with async_session() as session:
            async with session.begin():
                user = await User.get(tg_id=user_id, session=session)
                lobby = user.lobby
                count_personal_words = await HiddenWord.count_personal_words(session=session, user_id=user_id)
                print(f'TGID:{user.tg_id}, count: {count_personal_words}')
                if count_personal_words >= config.personal_word_count:
                    raise MaxWordCount()
                await HiddenWord.create(session=session, lobby_id=lobby.chat_id, word=word, user_id=user_id)
                return config.personal_word_count - count_personal_words - 1

    @classmethod
    async def is_not_active(cls, lobby_id: int, session: AsyncSession):
        is_active_timer = await CountdownTimer.is_exist(session=session, lobby_id=lobby_id)
        if is_active_timer:
            raise FillerAlreadyUsed()
        return True

    @classmethod
    async def close_chat(cls, chat_id: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                lobby = await Lobby.get(chat_id=chat_id, session=session)
                await lobby.game_running_state()

    @classmethod
    async def count_words(cls, chat_id: int, async_session=async_session_maker):
        async with async_session() as session:
            async with session.begin():
                return len(await HiddenWord.get_list(lobby_id=chat_id, session=session))

    @classmethod
    async def shuffle_and_trim_words(cls, chat_id: int, max_word_count: int, async_session=async_session_maker) -> list[str]:
        async with async_session() as session:
            async with session.begin():
                desired_count = max_word_count
                unique_values = (await session.execute(
                    select(HiddenWord.value).distinct().where(HiddenWord.lobby_id == chat_id).order_by(
                        func.random()))).scalars().all()

            if len(unique_values) < desired_count:
                desired_count = len(unique_values)
            return [unique_values[i] for i in range(0, desired_count)]
