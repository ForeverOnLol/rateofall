from common.views import CommonView
from debate_game.models import RoundInfo, Result
from telegram.consts import bot


class DebateGameTgView(CommonView):
    @staticmethod
    async def create(chat_id: int):
        await bot.send_message(chat_id=chat_id,
                               text=f'🎉 Добро пожаловать в игру *Дебаты*! 🌟 \n Введите команду /me, '
                                    f'чтобы стать участником. Всего может быть 2е участников')

    @staticmethod
    async def add_player(chat_id: int, username: str):
        await bot.send_message(chat_id=chat_id, text=f'{username} теперь является одним из дебатирующих 🌟')

    @staticmethod
    async def get_current_player(chat_id: int, username: str, position: str):
        styled_message = f'Отвечает *{username}* с позицией *{position}* 🎤'
        await bot.send_message(chat_id=chat_id, text=styled_message, parse_mode="Markdown")

    @staticmethod
    async def get_round_info(chat_id: int, round_info: RoundInfo):
        await bot.send_message(chat_id=chat_id,
                               text='**Тема раунда:**\n\n'
                                    f'*{round_info.word}*\n\n'
                                    f'{round_info.positions[0].user_name} -> {round_info.positions[0].position}\n'
                                    f'{round_info.positions[1].user_name} -> {round_info.positions[1].position}\n'
                                    f'Как только игроки будут готовы отвечать введите /next.',
                               parse_mode="Markdown")

    @staticmethod
    async def stop_answer(chat_id: int, username: str):
        await bot.send_message(chat_id=chat_id,
                               text=f'{username} *БОЛЬШЕ НЕ МОЖЕТ ГОВОРИТЬ* 🤐.')

    @staticmethod
    async def error(error_text, chat_id: int = 0):
        # await bot.send_message(chat_id=chat_id, text=error_text)
        print(f'{error_text}')

    @staticmethod
    async def result(chat_id: int, result: Result):
        player_scores = '\n'.join([f'{player.name} получает {player.score} баллов' for player in result.players])
        text = (
            f'🏆 *Итоги игры* 🏆:\n\n'
            f'{player_scores}\n\n'
            f'Победитель - *{result.winner_name}* 🎉'
        )

        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
