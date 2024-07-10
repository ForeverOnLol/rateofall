import re
from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


async def isint(s):
    try:
        s = int(s)
        return s
    except ValueError:
        return None


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):

            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class IntRangeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        text = message.text
        if text:
            digit = await isint(s=text)
            if (digit is not None) and (-10 <= digit <= 10):
                return True
        return False


class IsNotStartMessage(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        text = message.text
        if text == '/start':
            return False
        return True
