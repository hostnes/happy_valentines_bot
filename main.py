import logging

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyrogram import Client

from services.connect_server import valentines_service
from bot_creation import bot

from handlers.my_valentine import setup as my_valentines_handler_setup
from handlers.send_valentine import setup as send_valentine_handler_setup


logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())

api_id = 12552206
api_hash = "a374231734920c72574a978e3d6d867d"

app = Client("my_account", api_id=api_id, api_hash=api_hash)



async def startup(_):
    valentines_service.check_connect()


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    try:
        username = msg.from_user.username
        response = valentines_service.get_user(username)
        if len(response) == 0:
            username = msg.from_user.username
            user_data = {'telegram_id': msg.from_user.id,
                         'username': username}
            response = valentines_service.post_user(user_data)
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await msg.answer("Приветик. Как по мне самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того чтобы порадовать кого нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто прислал валентинку 💕",
                         reply_markup=inline_kb)
    except:
        await msg.answer('Для использывания бота требуеться сделать публичный свой username, '
                         'в случае если его у вас нету, добавить его.'
                         'После того как сделаете его публичным, еще раз пропишите /start')

@dp.message_handler(commands=["help"])
async def help(msg: types.Message):
    await msg.answer("Бот, при помощи которого вы можете отослать валентинку своему другу или подруге 💕\n"
                     "Создатель: @hostnes")


my_valentines_handler_setup(dp)
send_valentine_handler_setup(dp)

executor.start_polling(dp, skip_updates=True, on_startup=startup)
