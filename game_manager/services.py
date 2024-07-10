from aiogram.types import message

import config
from common.services import WordProviderService
from debate_game.services import DebateGameService
from game_manager.errors import CantRunWithoutWords, GameIsDone
from game_manager.models import GameTitles, Game
from lobby.controllers import LobbyController
from lobby.models import Lobby
from roa_game.services import RoaGameService


class GameManagerService():
    @staticmethod
    async def start(message: message, game_type: GameTitles):
        await WordProviderService().run_timer(message=message)
        if await WordProviderService().word_counter(message=message) <= 0:
            await Lobby.destroy(chat_id=message.chat.id)
            raise CantRunWithoutWords()

        if game_type == GameTitles.rate_off_all:
            max_word_count = config.max_word_count_roa
        elif game_type == GameTitles.debate:
            max_word_count = config.max_word_count_deb
        words_list = await WordProviderService.get_shuffled_trimed_words(message=message,
                                                                         max_word_count=max_word_count)

        if game_type == GameTitles.rate_off_all:
            await RoaGameService().start_roa(message=message, words_list=words_list)
        elif game_type == GameTitles.debate:
            await DebateGameService().start(message=message, words_list=words_list)

    @staticmethod
    async def next(message: message):
        game_name = await Game().get_game_name_by_lobby_id(lobby_id=message.chat.id)
        if game_name == GameTitles.rate_off_all.value:
            try:
                await RoaGameService().next_word(message=message)
            except GameIsDone:
                await LobbyController().destroy(message=message)
        elif game_name == GameTitles.debate.value:
            try:
                await DebateGameService().next(message=message)
            except GameIsDone:
                await LobbyController().destroy(message=message)


    @staticmethod
    async def set_score_roa(message: message):
        await RoaGameService().set_score(message=message)

    @staticmethod
    async def add_player_in_deb(message: message):
        await DebateGameService().add_player(message=message)
