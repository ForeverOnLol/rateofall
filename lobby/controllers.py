from aiogram.types import Message
from common.errors import UserAlreadyInLobby, UserNotInLobby
from lobby.views import LobbyView, WordProviderTgView
from lobby.errors import EmptyParty, FillerAlreadyUsed, FillerIsClosed, MaxWordCount, GameIsRunning, CantStopWhileFiller
from lobby.models import Lobby, WordProvider
from common.controllers import Controller
from roa_game.errors import GameIsNotExist


class LobbyController(Controller):
    def __init__(self, view: LobbyView = LobbyView(), model: Lobby = Lobby()):
        super().__init__(view, model)

    async def add_member(self, message: Message):
        user_id = message.from_user.id
        name = message.from_user.full_name
        username = message.from_user.username
        chat_id = message.chat.id
        try:
            await self.model.add_member(user_id=user_id, chat_id=chat_id, username=username, name=name)
            return await self.view.add_member(name=name)
        except UserAlreadyInLobby as e:
            return await self.view.error(error_text=e.msg, chat_id=chat_id)

    async def get_members_list(self, message: Message):
        chat_id = message.chat.id
        result = await self.model.get_members(chat_id=chat_id)
        if result:
            return await self.view.get_members(members_list=result)
        return await self.view.empty_members()

    async def destroy(self, message: Message):
        chat_id = message.chat.id
        try:
            await self.model.destroy(chat_id=chat_id)
            await self.view.destroy(chat_id=chat_id)
        except CantStopWhileFiller as e:
            return await self.view.error(error_text=e.msg, chat_id=chat_id)



class WordProviderController(Controller):
    def __init__(self, view: WordProviderTgView = WordProviderTgView(), model: WordProvider = WordProvider()):
        super().__init__(view, model)

    async def start(self, message: Message):
        chat_id = message.chat.id
        try:
            await self.model.start(lobby_id=chat_id)
            await self.view.start(chat_id=chat_id)
        except (EmptyParty, FillerAlreadyUsed, GameIsRunning) as e:
            raise e

    async def send_word(self, message: Message):
        user_id = message.from_user.id
        word = message.text

        try:
            count = await self.model.fill_word(user_id=user_id, word=word)
            await self.view.fill_word(remain_count=count, message=message)
        except (EmptyParty, FillerAlreadyUsed, UserNotInLobby, FillerIsClosed, MaxWordCount) as e:
            await self.view.error(error_text=e.msg, chat_id=message.chat.id)

    async def close_chat(self, message: Message):
        chat_id = message.chat.id
        await self.model.close_chat(chat_id=chat_id)
        return await self.view.timer_timeout(chat_id=chat_id)

    async def count_words(self, message: Message) -> int:
        chat_id = message.chat.id
        result = await self.model.count_words(chat_id=chat_id)
        return result

    async def shuffle_and_trim_words(self, message: Message, max_word_count: int) -> list[str]:
        chat_id = message.chat.id
        words = await self.model.shuffle_and_trim_words(chat_id=chat_id, max_word_count=max_word_count)
        return words
