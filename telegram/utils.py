from aiogram.types import message

from common.controllers import Controller
from lobby.controllers import WordProviderController
from roa_game.models import RoaGame
from .consts import bot



async def send_timer_timeout(chat_id):
    response = await WordProviderController().wait_timer(chat_id=chat_id)
    await bot.send_message(chat_id=chat_id, text=response)


async def send_roa_word(chat_id):
    response = await RoaGame().get_word()
    await bot.send_message(chat_id=chat_id, text=response)
