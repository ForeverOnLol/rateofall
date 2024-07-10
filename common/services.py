import abc
import asyncio
from abc import ABC

from aiogram.types import message

import config
from lobby.controllers import WordProviderController
from lobby.errors import EmptyParty, FillerAlreadyUsed, GameIsRunning
from lobby.views import WordProviderTgView


class GameService(ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError


class WordProviderService():
    @staticmethod
    async def run_timer(message: message):
        await WordProviderController().start(message=message)
        await asyncio.sleep(config.send_word_seconds)
        await WordProviderController().close_chat(message=message)

    @staticmethod
    async def word_counter(message: message) -> int:
        return await WordProviderController().count_words(message=message)

    @staticmethod
    async def get_shuffled_trimed_words(message: message, max_word_count: int) -> list[str]:
        return await WordProviderController().shuffle_and_trim_words(message=message, max_word_count=max_word_count)
