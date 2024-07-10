import asyncio

from aiogram.types import message, Message

from config import max_word_count_deb, sec_to_answer, sec_between_answers
from debate_game.controllers import DebateGameController
from debate_game.helpers import get_name_from_message
from debate_game.poll import PollManager
from game_manager.errors import GameIsDone
from lobby.errors import EmptyParty, FillerAlreadyUsed, GameIsRunning


class DebateGameService():
    @staticmethod
    async def start(message: Message, words_list: list[str]):
        await DebateGameController().create(message=message, words_list=words_list)

    @staticmethod
    async def add_player(message: Message):
        await DebateGameController().add_player(message=message)
        if await DebateGameController().get_players_count(message=message) == 2:
            await DebateGameController().start(message=message)
            await DebateGameController().new_round(message=message)
            await DebateGameController().get_round_info(message=message)


    @staticmethod
    async def next(message: Message):
        try:
            state = await DebateGameController().state(message=message)
            if state == 'ready_for_answer':
                for i in range(0, 2):
                    await DebateGameController().get_current_player(message=message)
                    await asyncio.sleep(sec_to_answer)
                    await DebateGameController().stop_answer(message=message)
                    if i != 1:
                        await asyncio.sleep(sec_between_answers)
                        await DebateGameController().switch_player(message=message)
                player_names = await DebateGameController().get_player_names(message=message)
                poll_id = await PollManager().send_poll(chat_id=message.chat.id, player_names=player_names)
                await DebateGameController().set_poll_id(message=message, poll_id=poll_id)
                await DebateGameController().finish_round(message=message)
            elif state == 'ready_for_next_word':
                poll_id = await DebateGameController().get_poll_id(message=message)
                result = await PollManager().get_poll_result(chat_id=message.chat.id, message_id=poll_id)
                for k, v in result.items():
                    await DebateGameController().set_score(message=message, score=v, player_name=k)
                await DebateGameController().next_word(message=message)
                await DebateGameController().new_round(message=message)
                await DebateGameController().get_round_info(message=message)
        except GameIsDone as e:
            await DebateGameController().result(message=message)
            raise e

        except (EmptyParty, FillerAlreadyUsed, GameIsRunning) as e:
            await DebateGameController().result(message=message)
            raise e
