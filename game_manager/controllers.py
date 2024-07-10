from dataclasses import dataclass

from aiogram.types import Message

from common.controllers import Controller
from game_manager.errors import CantRunWithoutWords
from game_manager.models import GameTitles
from game_manager.views import GameManagerTgView
from game_manager.services import GameManagerService
from lobby.errors import EmptyParty, GameIsRunning
from roa_game.errors import GameIsNotExist


class GameManagerController(Controller):
    '''
    Управляет игрой в лобби.
    '''

    def __init__(self, view: GameManagerTgView = GameManagerTgView(), model: GameManagerService = GameManagerService()):
        super().__init__(view, model)

    async def start_roa(self, message: Message):
        game_type = GameTitles.rate_off_all
        try:
            await self.model.start(message=message, game_type=game_type)
        except (CantRunWithoutWords, EmptyParty, GameIsRunning) as e:
            await self.view.error(e.msg, message.chat.id)

    async def next(self, message: Message):
        try:
            await self.model.next(message)
        except (CantRunWithoutWords, GameIsNotExist) as e:
            await self.view.error(e.msg, message.chat.id)

    async def set_score_roa(self, message: Message):
        try:
            await self.model.set_score_roa(message)
        except (CantRunWithoutWords) as e:
            await self.view.error(e.msg, message.chat.id)

    async def start_deb(self, message: Message):
        game_type = GameTitles.debate
        try:
            await self.model.start(message=message, game_type=game_type)
        except (CantRunWithoutWords, EmptyParty, GameIsRunning) as e:
            await self.view.error(e.msg, message.chat.id)

    async def add_player_in_deb(self, message: Message):
        await self.model.add_player_in_deb(message)
