import re

from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext

from aiogram import types, Dispatcher
from aiogram.types import KeyboardButton

from bot_creation import bot
from services.connect_server import valentines_service
from states.tier_state import ViewValentineState


async def get_my_valentines(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(recipient=callback.from_user.username)
    username = callback.from_user.username
    response = valentines_service.get_user(username)
    user_data = {'recipient': response[0]['id']}
    users_response = valentines_service.get_my_valentines(user_data)
    val_list = list(users_response)
    count = 0
    for i in users_response:
        if i['status'] == True:
            val_list.pop(count)
        else:
            count += 1
    await state.update_data(my_valentines=val_list)
    if len(val_list) == 0:
        await state.finish()
        await callback.message.answer("Hа данный момент у тебя нет непрочитанных валентинок 🎟\n"
                                      "Зайди попозже")
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await callback.message.answer("Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                         reply_markup=inline_kb)
    elif len(val_list) == 1:
        await state.set_state(ViewValentineState.GetValentines)
        await state.set_state(ViewValentineState.GetAnAnswer)
        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        reply_kb.add(KeyboardButton('Да'))
        reply_kb.add(KeyboardButton('Нет'))
        await callback.message.answer(f'У тебя есть {len(val_list)} не прочитанная валентинка, желаешь её посмотреть? 💕', reply_markup=reply_kb)

    elif len(val_list) >= 2 and len(val_list) <=4:
        await state.set_state(ViewValentineState.GetValentines)
        await state.set_state(ViewValentineState.GetAnAnswer)
        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        reply_kb.add(KeyboardButton('Да'))
        reply_kb.add(KeyboardButton('Нет'))
        await callback.message.answer(f'У тебя есть {len(val_list)} не прочитанная валентинка, желаешь её посмотреть? 💕', reply_markup=reply_kb)

    else:
        await state.set_state(ViewValentineState.GetValentines)
        await state.set_state(ViewValentineState.GetAnAnswer)
        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        reply_kb.add(KeyboardButton('Да'))
        reply_kb.add(KeyboardButton('Нет'))
        await callback.message.answer(f'У тебя есть {len(val_list)} не прочитанных валентинки, желаешь их посмотреть? 💕', reply_markup=reply_kb)


async def get_an_answer(message: types.Message, state: FSMContext):
    await state.set_state(ViewValentineState.ViewValentine)
    if message.text == 'Нет':
        await state.finish()
        await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
        inline_kb = types.InlineKeyboardMarkup(row_width=1)
        inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
        inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
        await message.answer("Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                         "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                         "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                         reply_markup=inline_kb)
    elif message.text == 'Да':
        get_data = await state.get_data()
        my_valentines = list(get_data['my_valentines'])
        if my_valentines[0]['is_publish'] == True:
            sender = f"@{my_valentines[0]['sender']}"
            valentine_id = my_valentines[0]['id']
        elif my_valentines[0]['is_publish'] == False:
            sender = 'Отправитель решил остаться в секретике 💒'
            valentine_id = my_valentines[0]['id']

        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

        len_list = len(my_valentines)
        if len_list > 2:
            reply_kb.add(KeyboardButton('Далее'))
            reply_kb.add(KeyboardButton('В главное меню'))
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n"
                                 f"У тебя еще {len(my_valentines) - 1} не прочитанные валентинки", reply_markup=reply_kb)
            await state.set_state(ViewValentineState.ViewValentine)


        elif len_list == 2:
            reply_kb.add(KeyboardButton('Далее'))
            reply_kb.add(KeyboardButton('В главное меню'))
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n"
                                 f"У тебя еще {len(my_valentines) - 1} не прочитанная валентинка", reply_markup=reply_kb)
            await state.set_state(ViewValentineState.ViewValentine)


        else:
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n")
            await state.finish()
            await message.answer('💞', reply_markup=types.ReplyKeyboardRemove())
            inline_kb = types.InlineKeyboardMarkup(row_width=1)
            inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
            inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
            await message.answer(
                "Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                reply_markup=inline_kb)

        my_valentines.pop(0)
        user_response = valentines_service.patch_valentines(valentine_id)
        await state.update_data(my_valentines=my_valentines)

    else:
        await message.answer('Нету такого варианта ответа')



async def view_valentines(message: types.Message, state: FSMContext):
    if message.text == 'Далее':
        get_data = await state.get_data()
        my_valentines = list(get_data['my_valentines'])
        if my_valentines[0]['is_publish'] == True:
            sender = f"@{my_valentines[0]['sender']}"
            valentine_id = my_valentines[0]['id']
        elif my_valentines[0]['is_publish'] == False:
            sender = 'Отправитель решил остаться в секретике 💒'
            valentine_id = my_valentines[0]['id']

        reply_kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)


        len_list = len(my_valentines)
        if len_list > 2:
            reply_kb.add(KeyboardButton('Далее'))
            reply_kb.add(KeyboardButton('В главное меню'))
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n"
                                 f"У тебя еще {len(my_valentines) - 1} не прочитанные валентинки",
                                 reply_markup=reply_kb)
            await state.set_state(ViewValentineState.ViewValentine)


        elif len_list == 2:
            reply_kb.add(KeyboardButton('Далее'))
            reply_kb.add(KeyboardButton('В главное меню'))
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n"
                                 f"У тебя еще {len(my_valentines) - 1} не прочитанная валентинка",
                                 reply_markup=reply_kb)
            await state.set_state(ViewValentineState.ViewValentine)

        else:
            if my_valentines[0]['file_id'] != "":
                await bot.send_photo(chat_id=message.from_user.id, photo=my_valentines[0]['file_id'])
            await message.answer(f"{my_valentines[0]['text']}\n\nОтправитель: {sender}\n\n", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            inline_kb = types.InlineKeyboardMarkup(row_width=1)
            inline_kb.add(types.InlineKeyboardButton("💒 Отправить валентинку 💒", callback_data="send_valentine"))
            inline_kb.add(types.InlineKeyboardButton("🎟 Просмотреть мои валентинки 🎟", callback_data="my_valentine"))
            await message.answer(
                "Приветик. Как по мне, самое время порадовать свою подругу или друга милой валентинкой💒\n\n"
                "Нажми '💒 Отправить валентинку 💒' для того, чтобы порадовать кого-нибудь 🎟\n\n"
                "Нажми '🎟 Просмотреть мои валентинки 🎟' вдруг тебе уже кто-то прислал валентинку 💕",
                reply_markup=inline_kb)
        my_valentines.pop(0)
        user_response = valentines_service.patch_valentines(valentine_id)
        await state.update_data(my_valentines=my_valentines)

    elif message.text == 'В главное меню':
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
        await message.answer('Такого варианта ответа нету')



def setup(dp: Dispatcher):
    dp.register_callback_query_handler(get_my_valentines, Text(equals="my_valentine"))

    dp.register_message_handler(get_an_answer, state=ViewValentineState.GetAnAnswer)
    dp.register_message_handler(view_valentines, state=ViewValentineState.ViewValentine)

