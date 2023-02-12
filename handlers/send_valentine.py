import hashlib
import re
from pprint import pprint

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext

from aiogram import types, Dispatcher
from aiogram.types import KeyboardButton, Message, ContentType
from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername

from services.connect_server import valentines_service
from states.tier_state import SendValentineState

from bot_creation import bot

from aiogram import Dispatcher, executor, types


dp = Dispatcher(bot, storage=MemoryStorage())




async def send_valentine(callback: types.CallbackQuery, state: FSMContext):
    try:
        username = callback.from_user.username
        await callback.message.delete()
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        inline_kb.add(types.InlineKeyboardButton("Да", callback_data="False"))
        inline_kb.add(types.InlineKeyboardButton("Нет", callback_data="True"))
        inline_kb.add(types.InlineKeyboardButton("В главное меню", callback_data="return"))
        await callback.message.answer('Желаете отправить анонимно?', reply_markup=inline_kb)
    except:
        await callback.message.answer('Для того чтобы отправить валентинку, требуется сделать публичный '
                                      'свой Usernsme, измените этот параметр в настройках и попробуйте еще раз')


async def get_publish(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(SendValentineState.GetUsername)
    await state.update_data(sender=callback.from_user.username)
    await state.update_data(is_publish=callback.data)
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    reply_kb.add(KeyboardButton('В главное меню'))
    await callback.message.answer('Введите никнэйм получателя: \n\nПримечание: username должен быть отправлен без @\n'
                                  'Пример: hostnes, yungchuggi', reply_markup=reply_kb)

async def get_username(message: types.Message, state: FSMContext):
        username = message.text
        if username == 'В главное меню':
            await state.finish()
            inline_kb = types.InlineKeyboardMarkup(row_width=1)
            await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
            inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
            inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
            await message.answer(
                "Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                reply_markup=inline_kb)
        else:
            if message.text == message.from_user.username:
                await message.answer('Вы не можете отправить валентинку самому себе.\nВведите другой username')
            else:
                result = re.match(r'[A-Za-z\d_]{5,32}$', username)
                if bool(result) == True:
                    await state.update_data(recipient=message.text)
                    await state.set_state(SendValentineState.GetPhotoAnswer)
                    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
                    reply_kb.add(KeyboardButton('Да'))
                    reply_kb.add(KeyboardButton('Нет'))
                    reply_kb.add(KeyboardButton('В главное меню'))
                    await message.answer('Хотите добавить фото?', reply_markup=reply_kb)
                else:
                    await message.answer("Не правильно вписан Username, попробуйте еще раз: ")


async def get_photo_answer(message: Message, state: FSMContext):
    text = message.text
    if text == 'В главное меню':
        await state.finish()
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await message.answer("Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                         reply_markup=inline_kb)
    elif text == 'Да':
        await state.set_state(SendValentineState.GetPhoto)
        await message.answer('Отправьте фото: ', reply_markup=types.ReplyKeyboardRemove())
    elif text == 'Нет':
        await state.set_state(SendValentineState.GetText)
        await state.update_data(file_id='')
        await message.answer('Добавьте текст к валентинке: ')
    else:
        await message.answer('Такого варианта ответа нету')


async def get_photo(message: types.Message, state: FSMContext):
    file_id = str(message.photo[-1].file_id)
    await state.update_data(file_id=file_id)
    await state.set_state(SendValentineState.GetText)
    reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    reply_kb.add(KeyboardButton('В главное меню'))
    await message.answer('Добавьте текст к валентинке: ', reply_markup=reply_kb)


async def get_text(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'В главное меню':
        await state.finish()
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await message.answer("Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                         reply_markup=inline_kb)
    else:
        await state.update_data(text=text)
        get_data = await state.get_data()
        await message.answer('Ваша валентинка отправлена 💕')
        await state.set_state()
        username = get_data['recipient']
        try:
            response = valentines_service.get_user(username)
            recipient_telegram_id = response[0]['telegram_id']
            recipient_id = response[0]['id']
            await bot.send_message(chat_id=recipient_telegram_id, text='Вам пришла новая валентинка 🎟')
        except:
            pass
        valentine_data = {
            'sender': get_data['sender'],
            'recipient': recipient_id,
            'is_publish': get_data['is_publish'],
            'text': get_data['text'],
            'file_id': get_data['file_id'],
        }
        response = valentines_service.post_valentines(valentine_data)
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await message.answer("Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                         reply_markup=inline_kb)


async def return_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.finish()
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    await callback.message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
    inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
    inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
    await callback.message.answer(
        "Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
        "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
        "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
        reply_markup=inline_kb)


def setup(dp: Dispatcher):
    """
    ОСНОВНЫЕ
    """
    dp.register_callback_query_handler(send_valentine, Text(equals="send_valentine"))
    dp.register_callback_query_handler(get_publish, Text(equals="True"))
    dp.register_callback_query_handler(get_publish, Text(equals="False"))

    dp.register_callback_query_handler(return_menu, Text(equals="return"))

    dp.register_message_handler(get_photo_answer, state=SendValentineState.GetPhotoAnswer)

    dp.register_message_handler(get_photo, state=SendValentineState.GetPhoto, content_types=ContentType.PHOTO)
    dp.register_message_handler(get_username, state=SendValentineState.GetUsername)
    dp.register_message_handler(get_text, state=SendValentineState.GetText)
    # dp.register_message_handler(get_user_data, state=SendValentineState.GetText)



