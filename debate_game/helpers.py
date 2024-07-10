from aiogram.types import Message


async def get_name_from_message(message: Message):
    word_arr = message.text.split()
    if len(word_arr) == 1:
        return message.from_user.full_name
    elif len(word_arr) > 1:
        return word_arr[1]