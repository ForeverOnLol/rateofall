from common.errors import UserNotInLobby
from db.core import async_session_maker
from .errors import EmptyParty, GameIsRunning
from lobby.errors import FillerIsClosed


def lobby_not_empty(func):
    async def inner(*args, **kwargs):
        from lobby.models import Lobby
        lobby_id = kwargs.get('lobby_id')
        if not lobby_id:
            raise Exception('В параметре функции нет lobby_id')
        async_session = async_session_maker
        async with async_session() as session:
            async with session.begin():
                lobby = await Lobby.is_exist(chat_id=lobby_id, session=session)
                if not lobby:
                    raise EmptyParty()
        res = await func(*args, **kwargs)
        return res

    return inner


def user_in_lobby(func):
    async def inner(*args, **kwargs):
        from common.models import User
        user_id = kwargs.get('user_id')
        if not user_id:
            raise Exception('В параметре функции нет user_id')
        async_session = async_session_maker
        async with async_session() as session:
            async with session.begin():
                user = await User.get(session=session, tg_id=user_id)
                if not user:
                    raise UserNotInLobby()
        res = await func(*args, **kwargs)
        return res

    return inner


def fill_word_state(func):
    async def inner(*args, **kwargs):
        from lobby.models import LobbyStates
        from common.models import User

        user_id = kwargs.get('user_id')
        if not user_id:
            raise Exception('В параметре функции нет user_id')

        async_session = async_session_maker
        async with async_session() as session:
            async with session.begin():
                lobby = (await User.get(session=session, tg_id=user_id)).lobby
                if not lobby:
                    raise EmptyParty()

                state = lobby.state
                if state != LobbyStates.word_filling.value:
                    raise FillerIsClosed()
        res = await func(*args, **kwargs)
        return res

    return inner


def wait_members_state(func):
    async def inner(*args, **kwargs):
        from lobby.models import LobbyStates
        from lobby.models import Lobby

        lobby_id = kwargs.get('lobby_id')
        if not lobby_id:
            raise Exception('В параметре функции нет lobby_id')

        async_session = async_session_maker
        async with async_session() as session:
            async with session.begin():
                lobby = await Lobby.get(chat_id=lobby_id, session=session)
                if not lobby:
                    raise EmptyParty()

                state = lobby.state
                if state != LobbyStates.wait_members.value:
                    raise GameIsRunning()
        res = await func(*args, **kwargs)
        return res

    return inner
