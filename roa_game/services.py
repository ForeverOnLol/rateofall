from aiogram.types import message

from lobby.errors import EmptyParty, FillerAlreadyUsed, GameIsRunning
from roa_game.controllers import RoaGameController, GraphController
from roa_game.errors import GameIsNotExist
from game_manager.errors import GameIsDone


class RoaGameService():
    @staticmethod
    async def start_roa(message: message, words_list: list[str]):
        try:
            await RoaGameController().start(message=message, words_list=words_list)
            await RoaGameController().get_current_word(message=message)
        except (EmptyParty, FillerAlreadyUsed, GameIsRunning) as e:
            print(e)

    @staticmethod
    async def next_word(message: message):
        try:
            await RoaGameController().round_stats(message=message)
            await RoaGameController().next_word(message=message)
            await RoaGameController().get_current_word(message=message)
        except (EmptyParty, FillerAlreadyUsed, GameIsRunning) as e:
            raise e
        except GameIsDone:
            data = await RoaGameController().result(message=message)
            await GraphController().result(message=message, round_data_list=data)
            raise GameIsDone()

    @staticmethod
    async def set_score(message: message):
        try:
            await RoaGameController().set_score(message=message)
        except (EmptyParty, FillerAlreadyUsed, GameIsRunning) as e:
            raise e
        except GameIsDone:
            await RoaGameController().result(message=message)
        except GameIsNotExist:
            pass
