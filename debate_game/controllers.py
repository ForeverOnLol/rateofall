from aiogram.types import Message

from common.controllers import Controller
from debate_game.models import DebateGame
from debate_game.views import DebateGameTgView


class DebateGameController(Controller):
    def __init__(self, view: DebateGameTgView = DebateGameTgView(), model: DebateGame = DebateGame()):
        super().__init__(view, model)

    async def create(self, message: Message, words_list: list[str]):
        chat_id = message.chat.id
        await self.model.create(chat_id=chat_id, words_list=words_list)
        await self.view.create(chat_id=chat_id)

    async def start(self, message: Message):
        chat_id = message.chat.id
        await self.model.start(chat_id=chat_id)

    async def get_players_count(self, message: Message):
        chat_id = message.chat.id
        return await self.model.get_players_count(chat_id=chat_id)

    async def set_score(self, message: Message, player_name, score):
        chat_id = message.chat.id
        await self.model.set_score(chat_id=chat_id, player_name=player_name, score=score)

    async def get_player_names(self, message: Message):
        chat_id = message.chat.id

        return await self.model.get_player_names(chat_id=chat_id)

    async def add_player(self, message: Message):
        chat_id = message.chat.id
        player_id = message.from_user.id
        player_name = message.from_user.full_name

        await self.model.add_player(player=(player_id, player_name), chat_id=chat_id)
        await self.view.add_player(chat_id=chat_id, username=player_name)

    async def next_word(self, message: Message):
        chat_id = message.chat.id
        await self.model.next_word(chat_id=chat_id)

    async def get_round_info(self, message: Message):
        chat_id = message.chat.id

        res = await self.model.get_round_info(chat_id=chat_id)
        await self.view.get_round_info(chat_id=chat_id, round_info=res)

    async def state(self, message: Message):
        chat_id = message.chat.id
        return await self.model.get_state(chat_id=chat_id)

    async def get_current_player(self, message: Message):
        chat_id = message.chat.id
        player_name, player_position = await self.model.get_current_player(chat_id=chat_id)
        await self.view.get_current_player(chat_id=chat_id, username=player_name, position=player_position)

    async def stop_answer(self, message: Message):
        chat_id = message.chat.id
        player_name, _ = await self.model.get_current_player(chat_id=chat_id)
        await self.view.stop_answer(chat_id=chat_id, username=player_name)

    async def switch_player(self, message: Message):
        chat_id = message.chat.id
        await self.model.switch_player(chat_id=chat_id)

    async def set_poll_id(self, message: Message, poll_id: int):
        chat_id = message.chat.id
        await self.model.set_poll_id(chat_id=chat_id, poll_id=poll_id)

    async def get_poll_id(self, message: Message):
        chat_id = message.chat.id
        return await self.model.get_poll_id(chat_id=chat_id)

    async def finish_round(self, message: Message):
        chat_id = message.chat.id
        await self.model.finish_round(chat_id=chat_id)

    async def new_round(self, message: Message):
        chat_id = message.chat.id
        return await self.model.set_state_new_round(chat_id=chat_id)

    async def result(self, message: Message):
        chat_id = message.chat.id
        result = await self.model.result(chat_id=chat_id)
        return await self.view.result(chat_id=chat_id, result=result)
