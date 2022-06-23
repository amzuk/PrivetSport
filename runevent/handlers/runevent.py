# from email.message import Message
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from runevent.base.init import bot, dp
from runevent.helpers.keyboard import kb_client, kb_admin
from runevent.dto.runevent import FSMadd, FSMAdmin
from runevent.logic import runevent


ID = None


# hiden moderator handler, moderator = telegram administrator
@dp.message_handler(commands='moderator', is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(
        message.from_user.id, 'What happend?', reply_markup=kb_admin)
    await message.delete()


# start/help handler
@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(
            message.from_user.id, "Welcome to RunEvent bot",
            reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply(
            "Communication with the bot in "
            "the PM, write to him:\nhttps://t.me/RunEventCS50x2022_bot"
        )


# add cancel handler
@dp.message_handler(state="*", commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("OK")


# list of all events handler
@dp.message_handler(commands=['events_list'])
async def event_list_command(message: types.message):
    await runevent.list_events(message)


# list of runners handler part2 finish (inline button)
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('show '))
async def callback_runner_list(cq: types.CallbackQuery):
    _, event_id, user_id = cq.data.split()
    runners = await runevent.list_runners(event_id)
    if len(runners) < 1:
        await bot.send_message(user_id, "list of runners is empty")
    else:
        await bot.send_message(
            user_id, str("\n".join(
                [f"Name of runner: {r[0]}   Note: {r[1]}"
                    for r in runners])))


# list of ruuners handler part1 (inline button)
@dp.message_handler(commands='runners_list')
async def def_callback_run1(message: types.Message):
     events = await runevent.list_events2()
     photo, name, date, distance, time, creator, id = 0, 1, 2, 3, 4, 5, 6
     for event in events:
        await bot.send_photo(
            message.from_user.id,
            event[photo],
            (f"{event[name]}\n"
             f"Date of Event: {event[date]}\n"
             f"Distance of run: {event[distance]}\n"
             f"Time of run: {event[time]}\n"
             f"Name of creator: {event[creator]}\n"
             f"Event ID: {event[id]}"))

        await bot.send_message(
            message.from_user.id,
            text='!!!!!!!',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    f'Show list of runners for Event ID = {event[id]}',
                    callback_data=f'show {event[id]} {message.from_user.id}')))


# create event handler part1
@dp.message_handler(commands='create_event', state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.photo.set()
    await message.reply("Load label of run")


# add event part2
@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id

    await FSMAdmin.next()
    await message.reply("enter event name")


# add event part3
@dp.message_handler(state=FSMAdmin.name_run)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name_run"] = message.text

    await FSMAdmin.next()
    await message.reply("enter event date")


# add event part 4
@dp.message_handler(state=FSMAdmin.date_run)
async def load_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["date_run"] = message.text

    await FSMAdmin.next()
    await message.reply("enter distance of event")


# add event handler part 5
@dp.message_handler(state=FSMAdmin.distance_run)
async def load_distance(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["distance_run"] = message.text

    await FSMAdmin.next()
    await message.reply("enter race duration")


# add event handler part6 finish
@dp.message_handler(state=FSMAdmin.time_run)
async def load_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["time_run"] = message.text
        data["name_creator"] = message.from_user.username

    async with state.proxy() as data:
        await runevent.add_event_command(state)
    await message.reply("Event added")
    await state.finish()


# delete event hadler part2 finish (only for moderator)
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await runevent.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(
        text=f'{callback_query.data.replace("del ", "")} deleted',
        show_alert=True)


# delete event handler part1 (only for moderator)
@dp.message_handler(commands='delete')
async def def_callback_run(message: types.Message):
    if message.from_user.id == ID:
        read = await runevent.list_events2()
        for x in read:
            await bot.send_photo(
                message.from_user.id,
                x[0],
                f"{x[1]}\nDate of Event: {x[2]}\nDistance "
                "of run: {x[3]}\n'Time of run: {x[4]}\n"
                "Name of creator: {x[5]}\n Event ID: {x[6]}",
            )
            await bot.send_message(
                message.from_user.id, text='!!!!!!!!',
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Delete {x[6]}',
                callback_data=f'del {x[6]}')))


# Delete runner handler part2 finish (inline button)
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('delete '))
async def callback_delete_runner(cq: types.CallbackQuery):
    _, event_id, user_id, username = cq.data.split()
    runners = await runevent.list_runners(event_id)
    if len(runners) < 1:
        await bot.send_message(user_id, "list of runners is empty")
    else:
        for runner in runners:
            if str(runner[0]) == username:
                del_data = (event_id, username)
                await runevent.del_runner_command(del_data)
                await bot.send_message(user_id, "Runner Deleted")
                return

        await bot.send_message(user_id, "You can only delete yourself")


# Delete ruuner handler part1 (inline button)
@dp.message_handler(commands='delete_runner')
async def def_callback_delete_runner(message: types.Message):
    # echo_callback = 'delete'
    # text_callback = 'Delete runners for Event ID = '
    events = await runevent.list_events2()
    photo, name, date, distance, time, creator, id = 0, 1, 2, 3, 4, 5, 6
    for event in events:
        await bot.send_photo(
            message.from_user.id,
            event[photo],
            (f"{event[name]}\n"
             f"Date of Event: {event[date]}\n"
             f"Distance of run: {event[distance]}\n"
             f"Time of run: {event[time]}\n"
             f"Name of creator: {event[creator]}\n"
             f"Event ID: {event[id]}"))

        await bot.send_message(
            message.from_user.id,
            text='!!!!!!!',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    f'Delete runners for Event ID = {event[id]}',
                    callback_data=f'delete {event[id]} {message.from_user.id} {message.from_user.username}')))



# Add runner handler part2 finish (inline button)
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('add '))
async def callback_add_runner(cq: types.CallbackQuery):
    _, event_id, user_id, username, notes = cq.data.split()
    runner = (event_id, username, notes)
    await runevent.add_runner_command(runner)
    await bot.send_message(user_id, "Runner added")


# add of ruuners handler part1 (FSM + inline button)
@dp.message_handler(commands='add_runner', state=None)
async def add_runner(message: types.Message):
    await FSMadd.run_notes.set()
    await message.reply("enter notes")


# add of ruuners handler part2 finish (FSM + inline button)
@dp.message_handler(state=FSMadd.run_notes)
async def def_callback_add_runner(message: types.Message, state: FSMContext):
    # echo_callback = 'delete'
    # text_callback = 'Delete runners for Event ID = '
    notes = message.text
    events = await runevent.list_events2()
    photo, name, date, distance, time, creator, id = 0, 1, 2, 3, 4, 5, 6
    for event in events:
        await bot.send_photo(
            message.from_user.id,
            event[photo],
            (f"{event[name]}\n"
             f"Date of Event: {event[date]}\n"
             f"Distance of run: {event[distance]}\n"
             f"Time of run: {event[time]}\n"
             f"Name of creator: {event[creator]}\n"
             f"Event ID: {event[id]}"))

        await bot.send_message(
            message.from_user.id,
            text='!!!!!!!',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    f'Write notes and push for ""Add runner where Event ID = {event[id]}',
                    callback_data=f'add {event[id]} {message.from_user.id} {message.from_user.username} {notes}')))

    await state.finish()
