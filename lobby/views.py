from aiogram.types import message

from common.views import CommonView
from config import bot_link, send_word_seconds
from telegram.consts import bot


class LobbyView(CommonView):
    @staticmethod
    async def add_member(name: str):
        return f'{name} добавлен в лобби'

    @staticmethod
    async def delete():
        return f'Спасибо за игру!'

    @staticmethod
    async def already_in(name: str):
        return f'{name} уже в лобби'

    @staticmethod
    async def get_members(members_list: []):
        members_str = "\n".join(str(member) for member in members_list)
        return "Список участников:\n" + members_str

    @staticmethod
    async def destroy(chat_id):
        await bot.send_message(chat_id=chat_id,
                               text='Спасибо за игру. Лобби расформировано. '
                                    'Список участников обнулён. Хорошего дня! 😊')

    @staticmethod
    async def error(error_text, chat_id: int):
        await bot.send_message(chat_id=chat_id, text=error_text)


class WordProviderTgView():
    @staticmethod
    async def start(chat_id: int):
        await bot.send_message(chat_id=chat_id,
                               text=f'📝 *Перейдите сюда* {bot_link} *и вводите темы, которые вас интересуют.*\n'
                                    f'🔒 *В ближайшие {send_word_seconds} секунд доступ закроется.* 🔒 \n'
                                    f'*Как только напишите темы - возвращайтесь.*')

    @staticmethod
    async def timer_timeout(chat_id: int):
        await bot.send_message(chat_id=chat_id, text=f'🔒Вы больше не можете присылать темы в ЛС бота🔒')

    @staticmethod
    async def error(error_text, chat_id: int):
        await bot.send_message(chat_id=chat_id, text=error_text)

    @staticmethod
    async def fill_word(message: message, remain_count):
        await message.answer(text=f'Записал. Оставшееся количество, которое вам доступно: {remain_count}')
