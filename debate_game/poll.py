import asyncio

from telegram.consts import bot


class PollManager():
    def __init__(self):
        pass
    @staticmethod
    async def send_poll(player_names: list[str], chat_id: int):
        message = await bot.send_poll(chat_id=chat_id, options=player_names, question='Какой участник понравился больше? Закончили голосовать /next.')
        return message.message_id

    @staticmethod
    async def get_poll_result(chat_id: int, message_id: int) -> dict:
        poll = await bot.stop_poll(chat_id=chat_id, message_id=message_id)
        result = {}
        for option in poll.options:
            result[option.text] = option.voter_count
        return result

# async def main():
#     message_id = await PollManager.send_poll(player_names=['Бибо', 'Бобо'], chat_id=-4040579394)
#     await asyncio.sleep(3)
#     res = await PollManager.get_poll_result(message_id=message_id, chat_id=-4040579394)
#     print(res)
# asyncio.run(main())
