from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

TOKEN = ''
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(skip_updates=True)
