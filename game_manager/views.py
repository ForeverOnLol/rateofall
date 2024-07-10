from aiogram.types import message

from common.views import CommonView
from lobby.controllers import WordProviderController
from telegram.consts import bot


class GameManagerTgView(CommonView):
    @staticmethod
    async def error(error_text, chat_id: int):
        await bot.send_message(chat_id=chat_id, text=error_text)