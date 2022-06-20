from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from base.init import bot, dp
from keyboards import kb_client
from dto.dto import FSMadd, FSMdel
from logic import logic


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(
            message.from_user.id, "Welcome to RunEvent bot",
            reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply(
            "Общение с ботом в ЛС, "
            "напишите ему:\nhttps://t.me/RunEventCS50x2022_bot"
        )


@dp.message_handler(commands=['add_runner'])
async def add_runner_command(message: types.Message):
    # await bot.send_message(message.from_user.id, 'we are add runner')
    await FSMadd.event_id.set()
    await message.reply("Enter event_id from Event list")


@dp.message_handler(state="*", commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("OK")


@dp.message_handler(state=FSMadd.event_id)
async def load_event_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["id"] = message.text
        data["name_runner"] = message.from_user.username

    await FSMadd.next()
    await message.reply("enter notes")


@dp.message_handler(state=FSMadd.run_notes)
async def load_notes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["notes"] = message.text

    async with state.proxy() as data:
        await logic.add_runner_command(state)
    await message.reply("Runner added")
    await state.finish()


# @dp.message_handler(commands=['delete_runner'])
# async def delete_runner_command(message: types.Message):
#     await bot.send_message(message.from_user.id, "we are delete runner")


@dp.message_handler(commands=['events_list'])
async def event_list_command(message: types.message):
    await logic.list_events(message)


# @dp.message_handler(state=FSMrunners.peoples_id)
# async def load_peoples_id(message: types.Message, state: FSMContext):
#     async with state.proxy() as data1:
#         data1["id"] = message.text

#     async with state.proxy() as data1:
#         await logic.list_runners(state)

#     await state.finish()


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('show '))
async def callback_runner_list(cq: types.CallbackQuery):
    _, event_id, user_id = cq.data.split()
    runners = await logic.list_runners(event_id)
    if len(runners) < 1:
        await bot.send_message(user_id, "list of runners is empty")
    else:
        await bot.send_message(
            user_id, str("\n".join(
                [f"Name of runner: {r[0]}, Note: {r[1]}"
                    for r in runners])))


@dp.message_handler(commands='runners_list')
async def def_callback_run1(message: types.Message):
     events = await logic.list_events2()
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


@dp.message_handler(commands=['delete_runner'])
async def add_del_runner_command(message: types.Message):
    # await bot.send_message(message.from_user.id, 'we are add runner')
    await FSMdel.ev_id.set()
    await message.reply("Enter event_id from Event list")


@dp.message_handler(state=FSMdel.ev_id)
async def load_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["id"] = message.text
        runners = await logic.list_runners(data['id'])
        username = message.from_user.username
        for runner in runners:
            # await bot.send_message(message.from_user.id, runner[0])
            # await bot.send_message(message.from_user.id, username)
            if str(runner[0]) == username:
                # await FSMdel.next()
                await message.reply(
                    "You in list. Do you want to delete yourself?   (y|n)")
                return await FSMdel.next()

        await bot.send_message(message.from_user.id,
                                "You can only delete yourself")
        await state.finish()
    # await FSMdel.next()
    # await bot.send_message(message.from_user.id,
                        #    'if you in list we will delete you?   (y/n)')


# @dp.message_handler(state=FSMdel.validate_runner)
# async def validate_runner(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         # print(data)
#         runners = await logic.list_runners(data['id'])
#         username = message.from_user.username
#         for runner in runners:
#             # await bot.send_message(message.from_user.id, runner[0])
#             # await bot.send_message(message.from_user.id, username)
#             if str(runner[0]) == username:
#                 # await FSMdel.next()
#                 await message.reply(
#                     "You in list. Do you want to delete yourself?   (y|n)")
#                 return await FSMdel.next()

#         await bot.send_message(message.from_user.id,
#                                 "You can only delete yourself")
#         await state.finish()
            # await FSMdel.next()
            # await message.reply("You in list")

    # await message.reply('if you in list we will delete you')


@dp.message_handler(state=FSMdel.del_runner)
async def delete_runner(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['key'] = message.text
        username = message.from_user.username
        # await bot.send_message(message.from_user.id, data['id'])
        if str(data['key']) == str('y'):
            del_data = (data['id'], username)
            await logic.del_runner_command(del_data)
            await bot.send_message(message.from_user.id, "Runner Deleted")
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, "Delete canceled")
            await state.finish()
