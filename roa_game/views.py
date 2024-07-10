from io import BytesIO

from PIL import Image
from aiogram.types import BufferedInputFile, Message

from common.views import CommonView
from roa_game.models import RoundData
from telegram.consts import bot


class RoaGameTgView(CommonView):
    @staticmethod
    async def start(chat_id: int):
        await bot.send_message(chat_id=chat_id,
                               text=f'🎉 Добро пожаловать в игру *Рейтинг всего*! 🌟')

    @staticmethod
    async def error(error_text, chat_id: int):
        await bot.send_message(chat_id=chat_id, text=error_text)

    @staticmethod
    async def set_score(message: Message):
        await message.answer(text=f'📝')

    @staticmethod
    async def current_topic(chat_id: int, topic: str):
        await bot.send_message(chat_id=chat_id,
                               text=f'🌟 *ТЕМА:* {topic}\n Напишите в чат, как вы оцениваете данное событие/предмет (число от -10 до 10).\nКак только все игроки поставят оценки /next.',
                               parse_mode='Markdown')

    @staticmethod
    async def round_stats(chat_id: int, round_data: RoundData):
        text = (f'🌟 *ТЕМА:* {round_data.word}\n'
                f'🎯 *Общий балл:* {round_data.total_score}\n\n')

        for user, score in round_data.users:
            text += f'💫 {user} поставил(а) {score}\n'
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

    @staticmethod
    async def result(chat_id: int, round_data: list[RoundData]):
        text = '🏆 *Результаты по игре:*\n'
        for data in round_data:
            text += f'🌟 {data.word} -> {data.total_score} баллов\n'
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')


class GraphTgView():
    @staticmethod
    async def plot(chat_id: int, bytes_png: BytesIO):
        photo = BufferedInputFile(bytes_png.read(), 'rateofall.png')
        return await bot.send_photo(chat_id=chat_id, photo=photo)
