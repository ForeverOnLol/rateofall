from aiogram import types
from aiogram.filters import Command
from common.controllers import CommandController
from telegram.filters import ChatTypeFilter, IntRangeFilter, IsNotStartMessage
from game_manager.controllers import GameManagerController
from lobby.controllers import LobbyController, WordProviderController
from .consts import bot, dp


@dp.message(Command('hi'), ChatTypeFilter(chat_type=["group"]))
async def hi(message: types.Message):
    print(f'TG::{message}')
    await CommandController().greeting(message=message)


@dp.message(Command('join'), ChatTypeFilter(chat_type=["group"]))
async def join(message: types.Message):
    print(f'TG::{message}')
    response = await LobbyController().add_member(message)
    await message.reply(text=response)


@dp.message(Command('party'), ChatTypeFilter(chat_type=["group"]))
async def party(message: types.Message):
    print(f'TG::{message}')
    response = await LobbyController().get_members_list(message)
    await message.reply(text=response)


@dp.message(Command('roa'), ChatTypeFilter(chat_type=["group"]))
async def roa_start(message: types.Message):
    print(f'TG::{message}')
    await GameManagerController().start_roa(message=message)


@dp.message(Command('stop'), ChatTypeFilter(chat_type=["group"]))
async def stop_handler(message: types.Message):
    print(f'TG::{message}')
    await LobbyController().destroy(message)


@dp.message(IsNotStartMessage(), ChatTypeFilter(chat_type=["private"]))
async def word_provider_sender_handler(message: types.Message):
    print(f'TG::{message}')
    await WordProviderController().send_word(message)


@dp.message(Command('start'), ChatTypeFilter(chat_type=["private"]))
async def word_provider_sender_handler(message: types.Message):
    print(f'TG::{message}')
    await CommandController().start_in_private(message)


@dp.message(Command('next'), ChatTypeFilter(chat_type=["group"]))
async def next_handler(message: types.Message):
    print(f'TG::{message}')
    await GameManagerController().next(message)


@dp.message(IntRangeFilter(), ChatTypeFilter(chat_type=["group"]))
async def score_input(message: types.Message):
    print(f'TG::{message}')
    await GameManagerController().set_score_roa(message)


# Дебаты
@dp.message(Command('deb'), ChatTypeFilter(chat_type=["group"]))
async def roa_start(message: types.Message):
    print(f'TG::{message}')
    await GameManagerController().start_deb(message=message)


@dp.message(Command('me'), ChatTypeFilter(chat_type=["group"]))
async def add_player_in_deb(message: types.Message):
    print(f'TG::{message}')
    await GameManagerController().add_player_in_deb(message=message)


async def run_bot() -> None:
    await dp.start_polling(bot)
