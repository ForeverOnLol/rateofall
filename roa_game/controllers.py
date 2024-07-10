from aiogram.types import Message

from common.controllers import Controller
from roa_game.graph import Plotter
from roa_game.models import RoaGame, RoundData
from roa_game.views import RoaGameTgView, GraphTgView


class RoaGameController(Controller):
    def __init__(self, view: RoaGameTgView = RoaGameTgView(), model: RoaGame = RoaGame()):
        super().__init__(view, model)

    async def start(self, message: Message, words_list: list[str]):
        chat_id = message.chat.id

        await self.model.start(chat_id=chat_id, words_list=words_list)
        await self.view.start(chat_id=chat_id)

    async def next_word(self, message: Message):
        chat_id = message.chat.id
        await self.model.next_word(chat_id=chat_id)

    async def get_current_word(self, message: Message):
        chat_id = message.chat.id
        word = await self.model.get_current_word(chat_id=chat_id)
        await self.view.current_topic(chat_id=chat_id, topic=word)

    async def set_score(self, message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        score = int(message.text)
        await self.model.set_score(user_id=user_id, chat_id=chat_id, score=score)
        await self.view.set_score(message=message)

    async def round_stats(self, message: Message):
        chat_id = message.chat.id

        round_data = await self.model.get_round_score(chat_id=chat_id)
        await self.view.round_stats(chat_id=chat_id, round_data=round_data)

    async def result(self, message: Message) -> list[RoundData]:
        chat_id = message.chat.id
        round_data = await self.model.result(chat_id=chat_id)
        await self.view.result(chat_id=chat_id, round_data=round_data)
        return round_data


class GraphController(Controller):
    def __init__(self, view: RoaGameTgView = GraphTgView(), model: RoaGame = Plotter()):
        super().__init__(view, model)

    async def result(self, message: Message, round_data_list: list[RoundData]):
        chat_id = message.chat.id

        bytes_png = await self.model.create_plot(round_data_list)
        await self.view.plot(chat_id=chat_id, bytes_png=bytes_png)
